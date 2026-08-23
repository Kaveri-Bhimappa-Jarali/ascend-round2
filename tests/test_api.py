from fastapi.testclient import TestClient

from app.main import app


def test_api_health() -> None:
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_api_summary_shape() -> None:
    with TestClient(app) as client:
        response = client.get("/api/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_resources"] == 0
    assert payload["compliance_score"] == 100.0
    assert "severity" in payload


def test_dashboard_loads() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "CloudCompliance Sentinel" in response.text
