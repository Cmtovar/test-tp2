# ChiPulse - Claude Code Project Instructions

## Project Overview
ChiPulse is a local event discovery platform for Chicago. FastAPI backend + React frontend.

## Tech Stack
- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL + PostGIS, Pydantic
- **Frontend**: React 19 + TypeScript, Vite, Tailwind CSS, React Router
- **Python deps**: see requirements.txt
- **Frontend deps**: see frontend/package.json
- **Config**: .env file (copy from .env.example)

## Project Structure
```
app/                        # Backend (FastAPI) — on main branch
  main.py                   # FastAPI app entry point
  config.py                 # Pydantic settings (env vars)
  database.py               # SQLAlchemy engine + session
  models/event.py           # SQLAlchemy ORM models
  routers/health.py         # GET /health
  routers/events.py         # /events routes
  schemas/event.py          # Pydantic response schemas

frontend/                   # Frontend (React)
  src/
    components/             # Shared components
      Layout.tsx            # App shell with Navbar + Outlet
      Navbar.tsx            # Top nav: ChiPulse | Home | My Events | Profile
      Toast.tsx             # Toast notification component
      EventCard.tsx         # Reusable event card (T-15)
    pages/                  # Route pages
      Home.tsx              # Home feed with event list (T-16)
      EventDetail.tsx       # Event detail page (/events/:id)
    api/events.ts           # API client with mock fallback
    types/event.ts          # TypeScript types matching backend EventOut
    data/mockEvents.ts      # Mock data (matches DB seed data)
    hooks/                  # Custom hooks (future)
    context/                # Auth context (future, T-22)
```

## API Contract
Backend returns events at `GET /api/events` with shape:
```json
{ "data": [Event, ...], "count": number }
```
Event fields: id, title, description, category, subcategory, start_datetime, end_datetime,
venue_name, venue_address, neighborhood, lat, lng, price_min, price_max, is_free,
ticket_url, source_url, source, image_url, status, tags, popularity

## Frontend Conventions
- **CSS**: Tailwind CSS (utility classes in JSX, no separate CSS files)
- **EventCard props**: `{ event: Event, isSaved?: boolean, onSaveToggle?: (id: string) => void }`
- **Source display**: Text below image: "sourced from: X"
- **Missing images**: Soft gray placeholder with landscape icon
- **Unimplemented nav links**: Show toast "Coming soon" instead of navigating
- **API fallback**: If backend is unreachable, mock data is used automatically

## Routes
| Path | Component | Status |
|------|-----------|--------|
| `/` | Home | Implemented |
| `/events/:id` | EventDetail | Implemented |
| `/my-events` | — | Toast only (T-28) |
| `/login` | — | Toast only (T-23) |
| `/register` | — | Toast only (T-24) |
| `/profile` | — | Toast only (T-25) |

## Git Workflow
- **Branch naming**: `Issue#-Feature-Type/Description`
- **One feature + one person per branch**
- **Main branch is protected** — no direct pushes
- **All changes require a Pull Request** with at least one reviewer
- Always create a new branch from latest `origin/main` before starting work

## Commands
- Run backend: `uvicorn app.main:app --reload`
- Run frontend: `cd frontend && npm run dev`
- Build frontend: `cd frontend && npm run build`
- Install backend deps: `pip install -r requirements.txt`
- Install frontend deps: `cd frontend && npm install`

## Parallel Session Coordination
When multiple Claude sessions work in parallel:
1. Each session should work on its own feature branch
2. Before creating a branch, run `git fetch origin` to see existing branches
3. Never work on the same files as another session without coordinating
4. Keep commits focused and small
5. Always pull latest main before branching: `git checkout main && git pull origin main`

## Team Roles
- PM: Gabriela
- Frontend/UX: Cristian
- Backend: Omar
- DevOps: Matthew
- Docs/QA: Jade

## AI Disclosure
Per course policy, document AI tool usage in PR descriptions.
