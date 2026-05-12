from app import main as main_module


class HealthySession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, _exc_type, _exc, _tb):
        return False

    async def execute(self, *_args, **_kwargs):
        return None


class UnhealthySession(HealthySession):
    async def execute(self, *_args, **_kwargs):
        raise RuntimeError("database unavailable")


def test_health_returns_healthy_when_database_is_connected(client, monkeypatch):
    monkeypatch.setattr(main_module, "AsyncSessionLocal", lambda: HealthySession())

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "healthy"
    assert payload["database"] == "connected"


def test_health_returns_503_when_database_is_unreachable(client, monkeypatch):
    monkeypatch.setattr(main_module, "AsyncSessionLocal", lambda: UnhealthySession())

    response = client.get("/health")

    assert response.status_code == 503
    payload = response.json()
    assert payload["status"] == "unhealthy"
    assert payload["database"] == "disconnected"
