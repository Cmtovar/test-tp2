import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault(
    "DATABASE_URL", "postgresql+asyncpg://test_user:test_pass@localhost:5432/chipulse_test"
)

from app.main import app


class FakeRow:
    def __init__(self, mapping: dict):
        self._mapping = mapping


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
