from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import date


class ProjectPlace(SQLModel, table=True):
    project_id: Optional[int] = Field(default=None, foreign_key="project.id", primary_key=True)
    place_id: Optional[int] = Field(default=None, foreign_key="place.id", primary_key=True)


class Place(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    external_id: int = Field(index=True)
    title: Optional[str] = None
    notes: Optional[str] = None
    visited: bool = Field(default=False)
    projects: List["Project"] = Relationship(back_populates="places", link_model=ProjectPlace)


class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    completed: bool = Field(default=False)
    places: List[Place] = Relationship(back_populates="projects", link_model=ProjectPlace)
