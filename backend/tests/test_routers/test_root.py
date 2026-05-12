def test_root_returns_service_metadata(client):
    response = client.get("/")

    assert response.status_code == 200
    payload = response.json()
    assert payload["service"] == "ChiPulse API"
    assert payload["version"] == "0.1.0"
