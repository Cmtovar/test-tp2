# ChiPulse Demo Setup Guide

Quick reference for getting the app running for demos. Two terminals needed.

## Prerequisites

- Python 3.11+
- Node.js 18+
- Ticketmaster API key (stored in `backend/.env`)

## 1. Backend (Terminal 1)

```bash
cd backend

# First time only: create virtual environment and install dependencies
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Create .env if it doesn't exist
cp .env.example .env
# Then edit .env and add your real TICKETMASTER_API_KEY
```

Your `backend/.env` should look like:

```
TICKETMASTER_API_KEY=your-real-key-here
# DATABASE_URL is optional — app works without a database
```

Start the server:

```bash
.venv/bin/uvicorn app.main:app --reload --port 8000
```

Verify it's working:

```bash
# In a separate terminal or browser:
curl http://localhost:8000/health
# Should return: {"status":"healthy","database":"not configured (using adapters)"}

curl http://localhost:8000/api/events | python3 -c "import sys,json; d=json.load(sys.stdin); print(f'{d[\"count\"]} events loaded')"
# Should return: 50 events loaded
```

## 2. Frontend (Terminal 2)

```bash
cd frontend

# First time only:
npm install

# Start dev server:
npm run dev
```

Open the URL shown in the terminal (usually `http://localhost:5173`).

**Important:** If port 5173 is busy, Vite picks the next available port. Check the terminal output for the actual URL.

## Troubleshooting

### Frontend shows no styling / unstyled text
- You're on the wrong port. Check which port Vite is actually using in its terminal output.
- Kill stale dev servers: `lsof -ti:5173,5174,5175 | xargs kill -9` then restart.

### Frontend shows mock data instead of real events
- Backend isn't running, or the frontend is on a port where the Vite proxy isn't active.
- Verify the backend is up: `curl http://localhost:8000/api/events`
- Verify the proxy works: `curl http://localhost:<vite-port>/api/events` — should return JSON, not HTML.

### Backend returns mock data (8 events instead of 50)
- `TICKETMASTER_API_KEY` is missing or wrong in `backend/.env`.
- Check: `grep TICKETMASTER backend/.env`

### "Module not found" errors
- Run `npm install` in `frontend/` or `.venv/bin/pip install -r requirements.txt` in `backend/`.

### Port already in use
- Kill the process on that port: `lsof -ti:<port> | xargs kill -9`

## How the data flows

```
Ticketmaster API  -->  FastAPI backend (:8000)  -->  Vite proxy  -->  React frontend (:5173)
                        /api/events                  /api -> :8000
```

- Backend fetches from Ticketmaster, caches for 1 hour
- If Ticketmaster fails, serves stale cache
- If no cache exists, falls back to 8 hardcoded mock events
- Frontend has its own mock fallback if the backend is completely unreachable

## API rate limits

- Free Ticketmaster tier: 5,000 calls/day
- With 1-hour cache: ~24 calls/day under normal use
- Cache resets on server restart — avoid restarting repeatedly during the demo

## .env is gitignored

The `backend/.env` file is NOT committed to the repo. Each team member needs to create their own from `.env.example` and add the API key.
