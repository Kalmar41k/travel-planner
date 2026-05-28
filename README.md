# Travel Planner API

Small FastAPI application for managing travel projects and places using the Art Institute of Chicago API for place validation.

Quick start (local):

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the app:

```bash
uvicorn app.main:app --reload
```

3. Open docs: http://localhost:8000/docs

API examples:

- Create a place:
```bash
curl -X POST http://127.0.0.1:8000/places/ \
  -H "Content-Type: application/json" \
  -d '{"external_id": 27992}'
```

- Create a project with place IDs:
```bash
curl -X POST http://127.0.0.1:8000/projects/ \
  -H "Content-Type: application/json" \
  -d '{"name":"Trip","places":[{"place_id":1},{"place_id":2}]}'
```

- Add multiple places to a project:
```bash
curl -X POST http://127.0.0.1:8000/projects/1/places \
  -H "Content-Type: application/json" \
  -d '{"place_ids":[3,4]}'
```

Docker:

```bash
docker build -t travel-planner .
docker run -p 8000:8000 travel-planner
```

Postman collection: `postman_collection.json`
