# ChiPulse Backend

ChiPulse backend — Chicago event discovery API.

## Prerequisites

- Python 3.11+
- PostgreSQL 15+ (13 works for local dev) with PostGIS 3.x

## Setup

```bash
# 1. Clone the repo and cd into backend
cd backend

# 2. Create a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# edit .env and set DATABASE_URL, e.g.
# DATABASE_URL=postgresql+asyncpg://postgres:<password>@localhost:5432/chipulse_dev

# 5. Create the database (in psql, connected as a superuser)
#    CREATE DATABASE chipulse_dev;
#    \c chipulse_dev
#    CREATE EXTENSION IF NOT EXISTS postgis;

# 6. Run migrations
python run_migrations.py

# 7. Seed sample data (15 Chicago events)
python seeds/seed_data.py
```

## Start the dev server

```bash
uvicorn app.main:app --reload
```

The API is served at http://localhost:8000.

## Endpoints

| Method | Path                     | Description                              |
|--------|--------------------------|------------------------------------------|
| GET    | `/health`                | Health check (verifies DB connectivity)  |
| GET    | `/api/events`            | List all events ordered by start time    |
| GET    | `/api/events/{event_id}` | Fetch one event by UUID                  |

Response shape for `/api/events`:

```json
{
  "data": [ { "id": "...", "title": "...", "lat": 41.8826, "lng": -87.6226, "...": "..." } ],
  "count": 15
}
```

`GET /api/events/{event_id}` returns the single event object (same shape as an item in `data`) or a 404:

```json
{ "error": { "code": "NOT_FOUND", "message": "Event not found" } }
```

## Project layout

```
backend/
├── app/
│   ├── main.py            # FastAPI app, CORS, router includes
│   ├── config.py          # pydantic-settings reading .env
│   ├── database.py        # async SQLAlchemy engine + session
│   ├── models/event.py    # SQLAlchemy ORM model
│   ├── schemas/event.py   # Pydantic response schemas
│   └── routers/events.py  # GET /api/events and /api/events/{id}
├── migrations/            # Raw SQL migrations, applied in order
├── seeds/                 # Seed SQL + loader script
├── run_migrations.py      # Migration runner
├── requirements.txt
└── .env.example
```
