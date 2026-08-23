"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.main import app


def client() -> TestClient:
    return TestClient(app)


def compliant_resource(resource_id: str = "bucket-compliant") -> dict:
    return {
        "provider": "AWS",
        "resource_type": "storage",
        "resource_id": resource_id,
        "resource_name": resource_id,
        "configuration": {
            "encryption_enabled": True,
            "logging_enabled": True,
            "public_access": False,
        },
    }


def non_compliant_resource(resource_id: str = "bucket-risky") -> dict:
    return {
        "provider": "AWS",
        "resource_type": "storage",
        "resource_id": resource_id,
        "resource_name": resource_id,
        "configuration": {
            "encryption_enabled": False,
            "logging_enabled": False,
            "public_access": True,
        },
    }


def test_health_check_endpoint() -> None:
    with client() as test_client:
        response = test_client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_evaluate_endpoint_compliant_resource() -> None:
    with client() as test_client:
        response = test_client.post("/api/resources/evaluate", json=[compliant_resource()])

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["status"] == "COMPLIANT"
    assert payload[0]["violations"] == []


def test_evaluate_endpoint_non_compliant_resource() -> None:
    with client() as test_client:
        response = test_client.post("/api/resources/evaluate", json=[non_compliant_resource()])

    assert response.status_code == 200
    payload = response.json()
    assert payload[0]["status"] == "NON_COMPLIANT"
    assert {violation["rule_id"] for violation in payload[0]["violations"]} == {
        "ENCRYPTION_REQUIRED",
        "LOGGING_REQUIRED",
        "PUBLIC_EXPOSURE_FORBIDDEN",
    }


def test_violations_endpoint_returns_persisted_violations() -> None:
    with client() as test_client:
        test_client.post("/api/resources/evaluate", json=[non_compliant_resource()])
        response = test_client.get("/api/violations")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 3
    assert payload[0]["provider"] == "AWS"
    assert "detected_at" in payload[0]


def test_compliance_summary_endpoint_counts_distinct_resources() -> None:
    with client() as test_client:
        test_client.post(
            "/api/resources/evaluate",
            json=[compliant_resource(), non_compliant_resource()],
        )
        response = test_client.get("/api/compliance/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_resources"] == 2
    assert payload["compliant_resources"] == 1
    assert payload["non_compliant_resources"] == 1
    assert payload["total_violations"] == 3
    assert payload["compliance_percentage"] == 50.0


def test_evaluate_endpoint_accepts_empty_resource_list() -> None:
    with client() as test_client:
        response = test_client.post("/api/resources/evaluate", json=[])

    assert response.status_code == 200
    assert response.json() == []


def test_evaluate_endpoint_validation_error() -> None:
    with client() as test_client:
        response = test_client.post("/api/resources/evaluate", json=[{"provider": "AWS"}])

    assert response.status_code == 422


def test_aws_and_gcp_like_resources_use_same_engine_contract() -> None:
    gcp_resource = compliant_resource("gcp-bucket")
    gcp_resource["provider"] = "GCP"

    with client() as test_client:
        response = test_client.post(
            "/api/resources/evaluate",
            json=[compliant_resource("aws-bucket"), gcp_resource],
        )

    assert response.status_code == 200
    assert [item["status"] for item in response.json()] == ["COMPLIANT", "COMPLIANT"]


def test_compliance_summary_ten_resources_scenario() -> None:
    resources = [compliant_resource(f"bucket-{i}") for i in range(9)]
    resources.append(non_compliant_resource("bucket-risky"))

    with client() as test_client:
        test_client.post("/api/resources/evaluate", json=resources)
        response = test_client.get("/api/compliance/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total_resources"] == 10
    assert payload["non_compliant_resources"] == 1
    assert payload["compliant_resources"] == 9
    assert payload["total_violations"] == 3
    assert payload["compliance_percentage"] == 90.0


def test_evaluate_endpoint_duplicate_resources_in_request() -> None:
    res = non_compliant_resource("bucket-dup")
    with client() as test_client:
        response = test_client.post("/api/resources/evaluate", json=[res, res])
        violations_resp = test_client.get("/api/violations")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert violations_resp.status_code == 200
    assert len(violations_resp.json()) == 3



