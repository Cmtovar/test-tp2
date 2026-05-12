import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

# DATABASE_URL MUST be set before importing app.main so that
# database.py initialises with a dummy URL instead of None.
# Do not move this block below any `from app.*` import.
os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test_user:test_pass@localhost:5432/chipulse_test"
)

from app.main import app  # noqa: E402


# ---------------------------------------------------------------------------
# Shared DB-stub helpers
# ---------------------------------------------------------------------------


class FakeRow:
    """Mimics a SQLAlchemy Row with a _mapping attribute."""

    def __init__(self, mapping: dict):
        self._mapping = mapping


class FakeResult:
    """Mimics the object returned by AsyncSession.execute()."""

    def __init__(self, rows=None, row=None):
        self._rows = rows or []
        self._row = row

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._row


class FakeSession:
    """Mimics AsyncSession well enough for router tests."""

    def __init__(self, *, rows=None, row=None, raises=None):
        self._rows = rows or []
        self._row = row
        self._raises = raises

    async def execute(self, *_args, **_kwargs):
        if self._raises is not None:
            raise self._raises
        return FakeResult(rows=self._rows, row=self._row)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_event_cache():
    """
    Reset the in-memory Ticketmaster cache before and after every test.

    The cache lives as module-level globals in app.routers.events.
    Without this reset, a test that populates or reads the cache would
    contaminate every test that runs after it, making test order matter.
    """
    import app.routers.events as ev

    ev._event_cache = []
    ev._cache_timestamp = 0.0
    yield
    ev._event_cache = []
    ev._cache_timestamp = 0.0


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_event_mapping() -> dict:
    return {
        "id": uuid4(),
        "title": "Chicago Jazz Night",
        "description": "Live jazz in downtown Chicago.",
        "category": "Music",
        "subcategory": "Jazz",
        "start_datetime": datetime(2026, 5, 10, 19, 0, tzinfo=UTC),
        "end_datetime": datetime(2026, 5, 10, 22, 0, tzinfo=UTC),
        "venue_name": "The Blue Note",
        "venue_address": "123 W Randolph St",
        "neighborhood": "Loop",
        "lat": 41.884,
        "lng": -87.63,
        "price_min": 20,
        "price_max": 50,
        "is_free": False,
        "ticket_url": "https://tickets.example.com/jazz-night",
        "source_url": "https://source.example.com/jazz-night",
        "source": "ticketmaster",
        "image_url": "https://images.example.com/jazz-night.jpg",
        "status": "active",
        "tags": ["music", "nightlife"],
        "popularity": 88,
    }
