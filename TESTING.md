# Testing Guide

This repository now includes automated tests for backend, frontend unit behavior, and frontend E2E flows.

## Test Stack

- **Backend**: `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-mock`, `httpx`
- **Frontend unit/integration**: `vitest`, `@testing-library/react`, `@testing-library/user-event`, `jsdom`
- **Frontend E2E**: `@playwright/test`

## Project Test Structure

```text
backend/
├── pytest.ini
└── tests/
    ├── conftest.py
    ├── test_models/
    │   └── test_event_model.py
    └── test_routers/
        ├── test_events.py
        └── test_health.py

frontend/
├── vitest.config.ts
├── playwright.config.ts
├── e2e/
│   ├── event-detail.spec.ts
│   └── home.spec.ts
└── src/__tests__/
    ├── setup.ts
    ├── api/events.test.ts
    ├── components/
    │   ├── EventCard.test.tsx
    │   └── Navbar.test.tsx
    └── pages/Home.test.tsx
```

## Run Tests Locally

1. Backend tests:

```bash
cd backend
DATABASE_URL=postgresql+asyncpg://test_user:test_pass@localhost:5432/chipulse_test pytest
```

2. Frontend lint + unit tests:

```bash
cd frontend
npm run lint
npm run test
```

3. Frontend coverage:

```bash
cd frontend
npm run test:coverage
```

4. Frontend E2E tests:

```bash
cd frontend
npx playwright install --with-deps chromium
npm run test:e2e -- --project=chromium
```

## CI Behavior

GitHub Actions (`.github/workflows/ci.yaml`) now runs on **push** and **pull_request**:

- **backend job**
  - installs backend dependencies
  - runs pytest with coverage
  - uploads `backend/coverage.xml` as an artifact
- **frontend job**
  - installs frontend dependencies
  - runs lint
  - runs Vitest coverage
  - builds frontend
  - uploads `frontend/coverage/lcov.info` as an artifact
- **e2e job**
  - installs Playwright Chromium
  - runs Playwright E2E specs
  - uploads Playwright report artifacts

## Notes and Caveats

- E2E tests use the frontend dev server and can pass using mock fallback data even if backend API is unavailable.
- You may see Vite proxy `ECONNREFUSED` logs during E2E runs when backend is not running; current app behavior falls back to mock data by design.
- Coverage is tracked and uploaded as artifacts, but no minimum threshold is currently enforced.
