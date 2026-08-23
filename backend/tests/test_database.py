"""Unit tests for database read/write repository operations."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.compliance.policies import PolicyDefinition
from app.compliance.rules import ConfigurableRule
from app.compliance.severity import Severity
from app.database.database import get_session, init_db
from app.database.models import ResourceDB, ViolationDB
from app.database.repository import ComplianceRepository
from app.models.resource import ResourceModel


def resource(resource_id: str = "bucket-1") -> ResourceModel:
    return ResourceModel(
        provider="AWS",
        resource_type="storage",
        resource_id=resource_id,
        resource_name=resource_id,
        configuration={"encryption_enabled": False},
    )


def violation(rule_id: str = "ENCRYPTION_REQUIRED"):
    policy = PolicyDefinition(
        id=rule_id,
        name="Encryption Required",
        resource_types=["storage"],
        field="encryption_enabled",
        operator="equals",
        expected=True,
        severity=Severity.HIGH,
        message="Resource encryption is disabled",
    )
    return ConfigurableRule(policy).evaluate(resource())


def test_resource_persistence_and_uniqueness() -> None:
    session = next(get_session())
    repository = ComplianceRepository(session)

    first = repository.save_resource(resource())
    second = repository.save_resource(
        ResourceModel(
            provider="AWS",
            resource_type="storage",
            resource_id="bucket-1",
            resource_name="renamed-bucket",
            configuration={"encryption_enabled": True},
        )
    )
    session.commit()

    assert first.id == second.id
    assert session.query(ResourceDB).count() == 1
    assert second.resource_name == "renamed-bucket"
    session.close()


def test_violation_persistence_and_uniqueness_by_replace() -> None:
    session = next(get_session())
    repository = ComplianceRepository(session)
    resource_row = repository.save_resource(resource())

    repository.replace_violations(resource_row, [violation()])
    repository.replace_violations(resource_row, [violation()])
    session.commit()

    assert session.query(ViolationDB).count() == 1
    session.close()


def test_sqlite_foreign_key_enforcement() -> None:
    session = next(get_session())
    session.add(
        ViolationDB(
            resource_db_id=9999,
            resource_id="missing",
            rule_id="ENCRYPTION_REQUIRED",
            severity="HIGH",
            message="orphan",
            status="FAIL",
        )
    )

    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()
    session.close()


def test_existing_data_survives_init_db() -> None:
    session = next(get_session())
    repository = ComplianceRepository(session)
    repository.save_resource(resource())
    session.commit()
    session.close()

    init_db()

    session = next(get_session())
    assert session.query(ResourceDB).count() == 1
    session.close()


def test_compliance_statistics_count_distinct_resources() -> None:
    session = next(get_session())
    repository = ComplianceRepository(session)
    resource_row = repository.save_resource(resource())
    repository.replace_violations(
        resource_row,
        [violation("ENCRYPTION_REQUIRED"), violation("PUBLIC_EXPOSURE_FORBIDDEN")],
    )
    session.commit()

    stats = repository.get_compliance_statistics()

    assert stats["total_resources"] == 1
    assert stats["non_compliant_resources"] == 1
    assert stats["total_violations"] == 2
    assert stats["compliance_percentage"] == 0.0
    session.close()
