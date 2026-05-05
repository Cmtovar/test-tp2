from app.database import get_session_or_none
from app.main import app
from tests.conftest import FakeRow


class FakeResult:
    def __init__(self, rows=None, row=None):
        self._rows = rows or []
        self._row = row

    def fetchall(self):
        return self._rows

    def fetchone(self):
        return self._row


class FakeSession:
    def __init__(self, *, rows=None, row=None):
        self._rows = rows or []
        self._row = row

    async def execute(self, *_args, **_kwargs):
        return FakeResult(rows=self._rows, row=self._row)


def test_list_events_returns_data_and_count(client, sample_event_mapping):
    async def override_get_session():
        yield FakeSession(rows=[FakeRow(sample_event_mapping)])

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 1
    assert len(payload["data"]) == 1
    assert payload["data"][0]["title"] == sample_event_mapping["title"]
    assert payload["data"][0]["source"] == sample_event_mapping["source"]


def test_list_events_returns_empty_collection_when_no_rows(client):
    async def override_get_session():
        yield FakeSession(rows=[])

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["count"] == 0
    assert payload["data"] == []


def test_get_event_returns_event_when_found(client, sample_event_mapping):
    async def override_get_session():
        yield FakeSession(row=FakeRow(sample_event_mapping))

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get(f"/api/events/{sample_event_mapping['id']}")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(sample_event_mapping["id"])
    assert payload["title"] == sample_event_mapping["title"]
    assert payload["source"] == sample_event_mapping["source"]


def test_get_event_returns_not_found_when_event_missing(client):
    async def override_get_session():
        yield FakeSession(row=None)

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "NOT_FOUND"
    assert payload["error"]["message"] == "Event not found"


def test_get_event_returns_422_for_invalid_uuid(client):
    response = client.get("/api/events/not-a-uuid")

    assert response.status_code == 422
