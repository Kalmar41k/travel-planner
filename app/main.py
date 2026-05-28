from fastapi import FastAPI, HTTPException, Depends, status
from typing import List, Optional
from sqlmodel import select, Session
from datetime import date
from pydantic import BaseModel

from .db import create_db_and_tables, get_session
from .models import Project, Place
from .artic_client import fetch_artwork

app = FastAPI(title="Travel Planner API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


class PlaceCreate(BaseModel):
    external_id: int


class PlaceReference(BaseModel):
    place_id: int


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: List[PlaceReference]


class ProjectUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    start_date: Optional[date]


class PlaceUpdate(BaseModel):
    notes: Optional[str]
    visited: Optional[bool]


def place_to_dict(place: Place) -> dict:
    return {
        "id": place.id,
        "external_id": place.external_id,
        "title": place.title,
        "notes": place.notes,
        "visited": place.visited,
    }


def project_to_dict(project: Project) -> dict:
    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "start_date": project.start_date,
        "completed": project.completed,
        "places": [place_to_dict(p) for p in project.places],
    }


async def create_place_from_external_id(external_id: int, session: Session) -> Place:
    data = await fetch_artwork(external_id)
    if not data:
        raise HTTPException(status_code=400, detail=f"External place {external_id} not found")

    title = data.get("data", {}).get("title")
    place = Place(external_id=external_id, title=title)
    session.add(place)
    session.commit()
    session.refresh(place)
    return place


@app.post("/places/", status_code=status.HTTP_201_CREATED)
async def create_place(payload: PlaceCreate, session: Session = Depends(get_session)):
    place = await create_place_from_external_id(payload.external_id, session)
    return place_to_dict(place)


@app.get("/places/", response_model=List[dict])
def list_all_places(session: Session = Depends(get_session)):
    places = session.exec(select(Place)).all()
    return [place_to_dict(p) for p in places]


@app.get("/places/{place_id}")
def get_place(place_id: int, session: Session = Depends(get_session)):
    place = session.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    return place_to_dict(place)


@app.patch("/places/{place_id}")
def update_place_entity(place_id: int, payload: PlaceUpdate, session: Session = Depends(get_session)):
    place = session.get(Place, place_id)
    if not place:
        raise HTTPException(status_code=404, detail="Place not found")
    if payload.notes is not None:
        place.notes = payload.notes
    if payload.visited is not None:
        place.visited = payload.visited
    session.add(place)
    session.commit()
    session.refresh(place)
    return place_to_dict(place)


@app.post("/projects/", status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, session: Session = Depends(get_session)):
    if not payload.places or len(payload.places) < 1:
        raise HTTPException(status_code=400, detail="Project must contain at least 1 place")
    if len(payload.places) > 10:
        raise HTTPException(status_code=400, detail="A project can have at most 10 places")

    place_ids = [p.place_id for p in payload.places]
    if len(set(place_ids)) != len(place_ids):
        raise HTTPException(status_code=400, detail="Duplicate places are not allowed in a project")

    places = []
    for place_id in place_ids:
        place = session.get(Place, place_id)
        if not place:
            raise HTTPException(status_code=400, detail=f"Place {place_id} not found")
        places.append(place)

    project = Project(name=payload.name, description=payload.description, start_date=payload.start_date)
    session.add(project)
    session.commit()
    session.refresh(project)

    for place in places:
        project.places.append(place)

    project.completed = all(p.visited for p in project.places)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project_to_dict(project)


@app.get("/projects/", response_model=List[dict])
def list_projects(session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    return [project_to_dict(p) for p in projects]


@app.get("/projects/{project_id}")
def get_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project_to_dict(project)


@app.put("/projects/{project_id}")
def update_project(project_id: int, payload: ProjectUpdate, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.start_date is not None:
        project.start_date = payload.start_date
    session.add(project)
    session.commit()
    session.refresh(project)
    return project_to_dict(project)


@app.delete("/projects/{project_id}", status_code=204)
def delete_project(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    visited = any(p.visited for p in project.places)
    if visited:
        raise HTTPException(status_code=400, detail="Cannot delete project with visited places")

    project.places = []
    session.delete(project)
    session.commit()
    return


class ProjectAddPlaces(BaseModel):
    place_ids: List[int]


@app.post("/projects/{project_id}/places", status_code=status.HTTP_201_CREATED)
def add_places_to_project(project_id: int, payload: ProjectAddPlaces, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if not payload.place_ids or len(payload.place_ids) < 1:
        raise HTTPException(status_code=400, detail="At least one place_id is required")
    if len(project.places) + len(payload.place_ids) > 10:
        raise HTTPException(status_code=400, detail="Project would exceed maximum number of places")

    place_ids = payload.place_ids
    if len(set(place_ids)) != len(place_ids):
        raise HTTPException(status_code=400, detail="Duplicate place_ids are not allowed")

    existing_ids = {p.id for p in project.places}
    new_ids = [pid for pid in place_ids if pid not in existing_ids]
    if len(existing_ids) + len(new_ids) > 10:
        raise HTTPException(status_code=400, detail="Project would exceed maximum number of places")

    added_places = []
    for place_id in new_ids:
        place = session.get(Place, place_id)
        if not place:
            raise HTTPException(status_code=400, detail=f"Place {place_id} not found")
        project.places.append(place)
        added_places.append(place)

    project.completed = all(p.visited for p in project.places) if project.places else False
    session.add(project)
    session.commit()
    session.refresh(project)
    return [place_to_dict(p) for p in added_places]


@app.get("/projects/{project_id}/places")
def list_project_places(project_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return [place_to_dict(p) for p in project.places]


@app.get("/projects/{project_id}/places/{place_id}")
def get_project_place(project_id: int, place_id: int, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    place = session.get(Place, place_id)
    if not project or not place or place not in project.places:
        raise HTTPException(status_code=404, detail="Place not found in project")
    return place_to_dict(place)


@app.patch("/projects/{project_id}/places/{place_id}")
def update_project_place(project_id: int, place_id: int, payload: PlaceUpdate, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    place = session.get(Place, place_id)
    if not project or not place or place not in project.places:
        raise HTTPException(status_code=404, detail="Place not found in project")
    if payload.notes is not None:
        place.notes = payload.notes
    if payload.visited is not None:
        place.visited = payload.visited
    session.add(place)
    session.commit()
    session.refresh(place)

    project.completed = all(p.visited for p in project.places) if project.places else False
    session.add(project)
    session.commit()
    session.refresh(project)
    return place_to_dict(place)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
