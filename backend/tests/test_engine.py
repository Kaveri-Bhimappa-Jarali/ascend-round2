"""Unit tests for compliance engine processing."""

from app.compliance.engine import ComplianceEngine
from app.compliance.policies import PolicyDefinition
from app.compliance.severity import Severity
from app.models.resource import ResourceModel


def policy(rule_id: str, resource_types: list[str], field: str, expected: bool, severity: Severity):
    return PolicyDefinition(
        id=rule_id,
        name=rule_id,
        resource_types=resource_types,
        field=field,
        operator="equals",
        expected=expected,
        severity=severity,
        message=f"{rule_id} failed",
    )


def resource(resource_type: str = "storage", configuration: dict | None = None) -> ResourceModel:
    return ResourceModel(
        provider="AWS",
        resource_type=resource_type,
        resource_id="resource-1",
        resource_name="resource-1",
        configuration=configuration or {},
    )


def test_engine_evaluates_multiple_failed_rules() -> None:
    engine = ComplianceEngine(
        policies=[
            policy("ENCRYPTION_REQUIRED", ["storage"], "encryption_enabled", True, Severity.HIGH),
            policy("LOGGING_REQUIRED", ["storage"], "logging_enabled", True, Severity.MEDIUM),
        ]
    )

    result = engine.evaluate(
        resource(configuration={"encryption_enabled": False, "logging_enabled": False})
    )

    assert result.status == "NON_COMPLIANT"
    assert [violation.rule_id for violation in result.violations] == [
        "ENCRYPTION_REQUIRED",
        "LOGGING_REQUIRED",
    ]


def test_engine_returns_compliant_when_rules_pass() -> None:
    engine = ComplianceEngine(
        policies=[policy("ENCRYPTION_REQUIRED", ["storage"], "encryption_enabled", True, Severity.HIGH)]
    )

    result = engine.evaluate(resource(configuration={"encryption_enabled": True}))

    assert result.status == "COMPLIANT"
    assert result.violations == []


def test_engine_handles_no_applicable_rules() -> None:
    engine = ComplianceEngine(
        policies=[policy("ENCRYPTION_REQUIRED", ["database"], "encryption_enabled", True, Severity.HIGH)]
    )

    result = engine.evaluate(resource(resource_type="vpc", configuration={"encryption_enabled": False}))

    assert result.status == "COMPLIANT"
    assert result.rule_results == []


def test_engine_evaluates_many_deterministically() -> None:
    engine = ComplianceEngine(
        policies=[policy("PUBLIC_EXPOSURE_FORBIDDEN", ["storage"], "public_access", False, Severity.HIGH)]
    )
    resources = [
        resource(configuration={"public_access": False}),
        resource(configuration={"public_access": True}),
    ]

    results = engine.evaluate_many(resources)

    assert [result.status for result in results] == ["COMPLIANT", "NON_COMPLIANT"]
