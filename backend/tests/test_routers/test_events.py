from app.database import get_session_or_none
from app.main import app
from tests.conftest import FakeRow, FakeResult, FakeSession  # noqa: F401 (FakeResult re-exported for clarity)


def test_list_events_returns_data_and_count(client, sample_event_mapping):
    async def override_get_session():
        yield FakeSession(rows=[FakeRow(sample_event_mapping)])

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

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
        app.dependency_overrides.pop(get_session_or_none, None)

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
        app.dependency_overrides.pop(get_session_or_none, None)

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
        # This UUID is an intentional sentinel that will never match any real event
        response = client.get("/api/events/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "NOT_FOUND"
    assert payload["error"]["message"] == "Event not found"


def test_get_event_returns_422_for_invalid_uuid(client):
    response = client.get("/api/events/not-a-uuid")

    assert response.status_code == 422


# ---------------------------------------------------------------------------
# API contract tests
# Verify the response *shape* so that schema changes are caught immediately.
# ---------------------------------------------------------------------------


def test_list_events_response_has_required_contract_keys(client, sample_event_mapping):
    """Response must always contain 'data' (list) and 'count' (int)."""
    async def override_get_session():
        yield FakeSession(rows=[FakeRow(sample_event_mapping)])

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    payload = response.json()
    assert "data" in payload, "Response must have a 'data' key"
    assert "count" in payload, "Response must have a 'count' key"
    assert isinstance(payload["data"], list), "'data' must be a list"
    assert isinstance(payload["count"], int), "'count' must be an int"
    assert payload["count"] == len(payload["data"]), "'count' must equal len(data)"


def test_list_events_each_event_has_required_fields(client, sample_event_mapping):
    """Every event in 'data' must expose the fields the frontend depends on."""
    async def override_get_session():
        yield FakeSession(rows=[FakeRow(sample_event_mapping)])

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    event = response.json()["data"][0]
    required_fields = {"id", "title", "source", "start_datetime"}
    for field in required_fields:
        assert field in event, f"Event must contain field '{field}'"


def test_not_found_error_response_has_required_contract_shape(client):
    """404 errors must always carry error.code and error.message."""
    async def override_get_session():
        yield FakeSession(row=None)

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events/00000000-0000-0000-0000-000000000001")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    payload = response.json()
    assert "error" in payload, "404 body must have an 'error' key"
    assert "code" in payload["error"], "error must have a 'code' field"
    assert "message" in payload["error"], "error must have a 'message' field"


# ---------------------------------------------------------------------------
# Fallback / resilience tests
# These protect against AWS or DB connectivity issues causing silent failures.
# ---------------------------------------------------------------------------


def test_list_events_falls_back_to_mock_when_db_raises(client):
    """When the DB session raises an exception, the API must still return 200."""
    async def override_get_session():
        yield FakeSession(raises=RuntimeError("DB unavailable"))

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert isinstance(payload["count"], int)


def test_list_events_falls_back_to_mock_when_no_db_configured(client):
    """When no DB session exists (session=None), the API must still return 200."""
    async def override_get_session():
        yield None

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    assert response.status_code == 200
    payload = response.json()
    assert "data" in payload
    assert isinstance(payload["count"], int)


def test_get_event_falls_back_to_mock_when_db_raises(client):
    """When the DB session raises, get_event must fall back gracefully (not return 500)."""
    async def override_get_session():
        yield FakeSession(raises=RuntimeError("DB unavailable"))

    app.dependency_overrides[get_session_or_none] = override_get_session

    try:
        response = client.get("/api/events/00000000-0000-0000-0000-000000000002")
    finally:
        app.dependency_overrides.pop(get_session_or_none, None)

    # The response must be 200 (found in fallback) or 404 (not found in fallback),
    # but never 500 — that would mean the fallback itself crashed.
    assert response.status_code in (200, 404)
