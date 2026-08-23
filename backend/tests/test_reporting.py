"""
Unit and integration tests for JSON compliance report generation,
reporting APIs, and database seeder.
"""

import json
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from app.database.database import get_session
from app.main import app
from app.models.resource import ResourceModel
from app.services.compliance_service import ComplianceService
from reports.report_generator import JSONReportGenerator
from seed_demo_data import seed_database


def client() -> TestClient:
    return TestClient(app)


def sample_aws_resource(resource_id: str = "aws-s3-1", compliant: bool = True) -> ResourceModel:
    return ResourceModel(
        provider="AWS",
        resource_type="storage",
        resource_id=resource_id,
        resource_name=resource_id,
        configuration={
            "encryption_enabled": compliant,
            "logging_enabled": compliant,
            "public_access": not compliant,
        },
    )


def sample_gcp_resource(resource_id: str = "gcp-db-1", compliant: bool = True) -> ResourceModel:
    return ResourceModel(
        provider="GCP",
        resource_type="database",
        resource_id=resource_id,
        resource_name=resource_id,
        configuration={
            "encryption_enabled": compliant,
            "logging_enabled": compliant,
            "public_access": not compliant,
        },
    )


def test_empty_database_report_edge_case() -> None:
    session = next(get_session())
    service = ComplianceService(session)

    report = service.generate_json_report(environment="test")

    assert report["metadata"]["environment"] == "test"
    assert "report_id" in report["metadata"]
    assert report["summary"]["total_resources"] == 0
    assert report["summary"]["compliant_resources"] == 0
    assert report["summary"]["non_compliant_resources"] == 0
    assert report["summary"]["compliance_percentage"] == 100.0
    assert report["resources"] == []
    assert report["violations"] == []
    session.close()


def test_report_structure_and_metrics_calculation(tmp_path: Path) -> None:
    session = next(get_session())
    service = ComplianceService(session)

    service.evaluate_resources([
        sample_aws_resource("aws-ok", compliant=True),
        sample_aws_resource("aws-fail", compliant=False),
        sample_gcp_resource("gcp-ok", compliant=True),
    ])

    report_file = tmp_path / "test_report.json"
    report = service.generate_json_report(output_path=report_file, environment="production")

    assert report["summary"]["total_resources"] == 3
    assert report["summary"]["compliant_resources"] == 2
    assert report["summary"]["non_compliant_resources"] == 1
    assert report["summary"]["total_violations"] == 3
    assert report["summary"]["compliance_percentage"] == 66.67
    assert len(report["resources"]) == 3
    assert len(report["violations"]) == 3

    assert report_file.exists()
    file_content = json.loads(report_file.read_text(encoding="utf-8"))
    assert file_content["summary"]["total_resources"] == 3
    session.close()


def test_json_report_generator_direct(tmp_path: Path) -> None:
    generator = JSONReportGenerator()
    data = {
        "summary": {
            "total_resources": 1,
            "compliant_resources": 0,
            "non_compliant_resources": 1,
            "total_violations": 1,
            "compliance_percentage": 0.0,
            "violations_by_severity": {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 0, "LOW": 0},
        },
        "resources": [{"provider": "AWS", "resource_id": "r1", "status": "NON_COMPLIANT"}],
        "violations": [{"provider": "AWS", "rule_id": "ENCRYPTION_REQUIRED", "severity": "HIGH"}],
    }

    report = generator.build_report(data, environment="staging")
    assert report["metadata"]["environment"] == "staging"
    assert report["summary"]["violations_by_severity"]["HIGH"] == 1

    export_path = tmp_path / "direct_export.json"
    generator.export_json(report, export_path)
    assert export_path.exists()


def test_get_json_report_api_endpoint() -> None:
    with client() as test_client:
        test_client.post(
            "/api/resources/evaluate",
            json=[
                {
                    "provider": "AWS",
                    "resource_type": "storage",
                    "resource_id": "api-bucket",
                    "resource_name": "api-bucket",
                    "configuration": {"encryption_enabled": True, "logging_enabled": True, "public_access": False},
                }
            ],
        )

        response = test_client.get("/api/reports/json")

    assert response.status_code == 200
    payload = response.json()
    assert "metadata" in payload
    assert "summary" in payload
    assert payload["summary"]["total_resources"] == 1
    assert payload["summary"]["compliance_percentage"] == 100.0


def test_get_pdf_report_api_endpoint() -> None:
    with client() as test_client:
        test_client.post(
            "/api/resources/evaluate",
            json=[
                {
                    "provider": "AWS",
                    "resource_type": "storage",
                    "resource_id": "api-bucket",
                    "resource_name": "api-bucket",
                    "configuration": {"encryption_enabled": True, "logging_enabled": True, "public_access": False},
                }
            ],
        )

        response = test_client.get("/api/reports/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert len(response.content) > 0


def test_demo_seeder_execution() -> None:
    summary = seed_database(reset=True, export_report=False)

    assert summary["total_resources"] == 6
    assert summary["compliant_resources"] == 2
    assert summary["non_compliant_resources"] == 4
    assert summary["total_violations"] == 7
