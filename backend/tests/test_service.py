"""Unit tests for the compliance service orchestration layer."""

from app.database.database import get_session
from app.database.models import ResourceDB, ViolationDB
from app.models.resource import ResourceModel
from app.services.compliance_service import ComplianceService


def resource(resource_id: str, configuration: dict) -> ResourceModel:
    return ResourceModel(
        provider="AWS",
        resource_type="storage",
        resource_id=resource_id,
        resource_name=resource_id,
        configuration=configuration,
    )


def test_service_evaluates_and_persists_resources_and_violations() -> None:
    session = next(get_session())
    service = ComplianceService(session)

    results = service.evaluate_resources(
        [
            resource(
                "bucket-risky",
                {
                    "encryption_enabled": False,
                    "logging_enabled": False,
                    "public_access": True,
                },
            )
        ]
    )

    assert results[0].status == "NON_COMPLIANT"
    assert session.query(ResourceDB).count() == 1
    assert session.query(ViolationDB).count() == 3
    session.close()


def test_service_clears_stale_violations_when_resource_becomes_compliant() -> None:
    session = next(get_session())
    service = ComplianceService(session)

    service.evaluate_resources(
        [
            resource(
                "bucket-flips",
                {
                    "encryption_enabled": False,
                    "logging_enabled": False,
                    "public_access": True,
                },
            )
        ]
    )
    service.evaluate_resources(
        [
            resource(
                "bucket-flips",
                {
                    "encryption_enabled": True,
                    "logging_enabled": True,
                    "public_access": False,
                },
            )
        ]
    )

    assert session.query(ResourceDB).count() == 1
    assert session.query(ViolationDB).count() == 0
    session.close()


def test_service_summary() -> None:
    session = next(get_session())
    service = ComplianceService(session)

    service.evaluate_resources(
        [
            resource(
                "bucket-ok",
                {
                    "encryption_enabled": True,
                    "logging_enabled": True,
                    "public_access": False,
                },
            ),
            resource(
                "bucket-risky",
                {
                    "encryption_enabled": False,
                    "logging_enabled": False,
                    "public_access": True,
                },
            ),
        ]
    )

    summary = service.get_summary()

    assert summary["total_resources"] == 2
    assert summary["non_compliant_resources"] == 1
    assert summary["total_violations"] == 3
    session.close()
