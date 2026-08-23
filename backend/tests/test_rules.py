"""Unit tests for compliance rules checking logic."""

import pytest
from pydantic import ValidationError

from app.compliance.policies import PolicyDefinition
from app.compliance.rules import ConfigurableRule
from app.compliance.severity import Severity
from app.models.resource import ResourceModel


def make_policy(
    rule_id: str,
    field: str,
    expected: bool,
    severity: Severity = Severity.HIGH,
    operator: str = "equals",
) -> PolicyDefinition:
    return PolicyDefinition(
        id=rule_id,
        name=rule_id.replace("_", " ").title(),
        resource_types=["storage"],
        field=field,
        operator=operator,
        expected=expected,
        severity=severity,
        message=f"{field} failed",
    )


def make_resource(configuration: dict) -> ResourceModel:
    return ResourceModel(
        provider="AWS",
        resource_type="storage",
        resource_id="bucket-1",
        resource_name="bucket-1",
        configuration=configuration,
    )


def test_encryption_required_rule_passes() -> None:
    result = ConfigurableRule(make_policy("ENCRYPTION_REQUIRED", "encryption_enabled", True)).evaluate(
        make_resource({"encryption_enabled": True})
    )

    assert result.status == "PASS"


def test_encryption_required_rule_fails() -> None:
    result = ConfigurableRule(make_policy("ENCRYPTION_REQUIRED", "encryption_enabled", True)).evaluate(
        make_resource({"encryption_enabled": False})
    )

    assert result.status == "FAIL"
    assert result.severity == Severity.HIGH


def test_logging_required_rule_passes() -> None:
    result = ConfigurableRule(
        make_policy("LOGGING_REQUIRED", "logging_enabled", True, Severity.MEDIUM)
    ).evaluate(make_resource({"logging_enabled": True}))

    assert result.status == "PASS"
    assert result.severity == Severity.MEDIUM


def test_logging_required_rule_fails() -> None:
    result = ConfigurableRule(
        make_policy("LOGGING_REQUIRED", "logging_enabled", True, Severity.MEDIUM)
    ).evaluate(make_resource({"logging_enabled": False}))

    assert result.status == "FAIL"
    assert result.severity == Severity.MEDIUM


def test_public_exposure_forbidden_rule_passes() -> None:
    result = ConfigurableRule(make_policy("PUBLIC_EXPOSURE_FORBIDDEN", "public_access", False)).evaluate(
        make_resource({"public_access": False})
    )

    assert result.status == "PASS"


def test_public_exposure_forbidden_rule_fails() -> None:
    result = ConfigurableRule(make_policy("PUBLIC_EXPOSURE_FORBIDDEN", "public_access", False)).evaluate(
        make_resource({"public_access": True})
    )

    assert result.status == "FAIL"
    assert result.message == "public_access failed"


def test_missing_field_fails_safely() -> None:
    result = ConfigurableRule(make_policy("ENCRYPTION_REQUIRED", "encryption_enabled", True)).evaluate(
        make_resource({})
    )

    assert result.status == "FAIL"
    assert result.actual is None


def test_not_equals_operator() -> None:
    policy = make_policy("NOT_DEFAULT", "is_default", True, operator="not_equals")
    result = ConfigurableRule(policy).evaluate(make_resource({"is_default": False}))

    assert result.status == "PASS"


def test_invalid_operator_policy_fails_validation() -> None:
    with pytest.raises(ValidationError):
        make_policy("BAD_OPERATOR", "field", True, operator="contains")


def test_duplicate_policy_rule_ids_raises_error(tmp_path) -> None:
    from app.compliance.policies import load_policies

    json_content = """{
      "rules": [
        {
          "id": "DUP_RULE",
          "name": "Rule 1",
          "resource_types": ["storage"],
          "field": "encryption_enabled",
          "operator": "equals",
          "expected": true,
          "severity": "HIGH",
          "message": "Failed"
        },
        {
          "id": "DUP_RULE",
          "name": "Rule 2",
          "resource_types": ["storage"],
          "field": "logging_enabled",
          "operator": "equals",
          "expected": true,
          "severity": "LOW",
          "message": "Failed"
        }
      ]
    }"""
    policy_file = tmp_path / "duplicate_policies.json"
    policy_file.write_text(json_content, encoding="utf-8")

    with pytest.raises(ValueError, match="Duplicate policy rule IDs"):
        load_policies(policy_file)

