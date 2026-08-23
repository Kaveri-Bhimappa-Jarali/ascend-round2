from pathlib import Path

from fastapi.testclient import TestClient

from app.db.database import get_session
from app.db.models import ResourceSnapshot, Violation
from app.main import app


def clear_tables() -> None:
    with get_session() as session:
        session.query(Violation).delete()
        session.query(ResourceSnapshot).delete()
        session.commit()


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


def test_scan_not_implemented() -> None:
    with TestClient(app) as client:
        response = client.post("/api/scan")

    assert response.status_code == 501
    assert response.json()["status"] == "not_implemented"


def test_summary_counts_distinct_failed_resources() -> None:
    clear_tables()

    with get_session() as session:
        resource = ResourceSnapshot(
            provider="aws",
            resource_type="s3_bucket",
            resource_id="customer-data",
            name="customer-data",
            region="us-east-1",
            configuration_json="{}",
        )
        session.add(resource)
        session.flush()
        session.add_all(
            [
                Violation(
                    resource_snapshot_id=resource.id,
                    rule_id="AWS-S3-001",
                    status="FAIL",
                    severity="HIGH",
                    message="S3 encryption disabled",
                ),
                Violation(
                    resource_snapshot_id=resource.id,
                    rule_id="AWS-S3-002",
                    status="FAIL",
                    severity="CRITICAL",
                    message="S3 public access enabled",
                ),
            ]
        )
        session.commit()

    with TestClient(app) as client:
        response = client.get("/api/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_resources"] == 1
    assert payload["violations"] == 2
    assert payload["compliant_resources"] == 0
    assert payload["compliance_score"] == 0.0

    clear_tables()


def test_violations_include_resource_identity() -> None:
    clear_tables()

    with get_session() as session:
        resource = ResourceSnapshot(
            provider="gcp",
            resource_type="gcs_bucket",
            resource_id="customer-data",
            name="customer-data",
            region="asia-south1",
            configuration_json="{}",
        )
        session.add(resource)
        session.flush()
        session.add(
            Violation(
                resource_snapshot_id=resource.id,
                rule_id="GCP-GCS-001",
                status="FAIL",
                severity="HIGH",
                message="GCS bucket security requirement failed",
            )
        )
        session.commit()

    with TestClient(app) as client:
        response = client.get("/api/violations")

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["provider"] == "gcp"
    assert payload[0]["resource_type"] == "gcs_bucket"
    assert payload[0]["resource_id"] == "customer-data"

    clear_tables()


def test_dashboard_loads() -> None:
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "CloudCompliance Sentinel" in response.text


def test_dashboard_loads_outside_project_root(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)

    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert "CloudCompliance Sentinel" in response.text
