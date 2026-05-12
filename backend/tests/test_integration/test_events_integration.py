from datetime import UTC, datetime
from uuid import UUID

from app.database import get_session_or_none
from app.main import app
from app.routers import events as events_module


def _normalized_event(event_id: UUID, title: str = "Integration Test Event") -> dict:
    return {
        "id": event_id,
        "title": title,
        "description": "Integration event",
        "category": "music",
        "subcategory": "jazz",
        "start_datetime": datetime(2026, 6, 1, 19, 0, tzinfo=UTC),
        "end_datetime": datetime(2026, 6, 1, 22, 0, tzinfo=UTC),
        "venue_name": "Test Venue",
        "venue_address": "123 Test St, Chicago, IL",
        "neighborhood": "Loop",
        "lat": 41.88,
        "lng": -87.63,
        "price_min": 0,
        "price_max": 0,
        "is_free": True,
        "ticket_url": "https://example.com/tickets",
        "source_url": "https://example.com/source",
        "source": "ticketmaster",
        "image_url": "https://example.com/image.jpg",
        "status": "active",
        "tags": ["music"],
        "popularity": 75,
    }


class FakeTicketmasterAdapter:
    raw_events: list[dict] = []
    should_raise: bool = False

    def __init__(self, _api_key: str):
        pass

    def fetch_events(self):
        if self.should_raise:
            raise RuntimeError("Ticketmaster unavailable")
        return self.raw_events

    def normalize_event(self, raw_event: dict) -> dict:
        return raw_event

    def validate_event(self, normalized_event: dict) -> bool:
        required = ("id", "title", "start_datetime", "source")
        return all(normalized_event.get(k) for k in required)


def test_list_events_uses_ticketmaster_when_db_session_is_none(client, monkeypatch):
    event_id = UUID("11111111-1111-1111-1111-111111111111")

    async def override_get_session():
        yield None

    FakeTicketmasterAdapter.raw_events = [_normalized_event(event_id)]
    FakeTicketmasterAdapter.should_raise = False
    monkeypatch.setattr(events_module, "TicketmasterAdapter", FakeTicketmasterAdapter)
    monkeypatch.setattr(events_module.settings, "ticketmaster_api_key", "fake-key")
    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert payload["data"][0]["id"] == str(event_id)
    assert payload["data"][0]["title"] == "Integration Test Event"


def test_get_event_uses_stale_cache_when_ticketmaster_later_fails(client, monkeypatch):
    event_id = UUID("22222222-2222-2222-2222-222222222222")

    async def override_get_session():
        yield None

    monkeypatch.setattr(events_module, "TicketmasterAdapter", FakeTicketmasterAdapter)
    monkeypatch.setattr(events_module.settings, "ticketmaster_api_key", "fake-key")
    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        FakeTicketmasterAdapter.raw_events = [_normalized_event(event_id, title="Cached Event")]
        FakeTicketmasterAdapter.should_raise = False
        list_response = client.get("/api/events")
        assert list_response.status_code == 200
        assert list_response.json()["count"] == 1

        FakeTicketmasterAdapter.should_raise = True
        detail_response = client.get(f"/api/events/{event_id}")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    assert detail_response.status_code == 200
    payload = detail_response.json()
    assert payload["id"] == str(event_id)
    assert payload["title"] == "Cached Event"


def test_list_events_filters_invalid_normalized_events(client, monkeypatch):
    valid_id = UUID("33333333-3333-3333-3333-333333333333")

    async def override_get_session():
        yield None

    valid_event = _normalized_event(valid_id, title="Valid Event")
    invalid_event = _normalized_event(UUID("44444444-4444-4444-4444-444444444444"), title="")

    FakeTicketmasterAdapter.raw_events = [valid_event, invalid_event]
    FakeTicketmasterAdapter.should_raise = False
    monkeypatch.setattr(events_module, "TicketmasterAdapter", FakeTicketmasterAdapter)
    monkeypatch.setattr(events_module.settings, "ticketmaster_api_key", "fake-key")
    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert len(payload["data"]) == 1
    assert payload["data"][0]["id"] == str(valid_id)
