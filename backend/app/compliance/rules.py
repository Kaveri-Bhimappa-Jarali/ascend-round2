"""Provider-agnostic compliance rule evaluation."""

from dataclasses import dataclass
from typing import Any

from app.compliance.policies import PolicyDefinition
from app.compliance.severity import Severity
from app.models.resource import ResourceModel


@dataclass(frozen=True)
class RuleEvaluation:
    rule_id: str
    rule_name: str
    status: str
    severity: Severity
    message: str
    field: str
    expected: Any
    actual: Any

    @property
    def passed(self) -> bool:
        return self.status == "PASS"


class ConfigurableRule:
    """Evaluates one policy definition against a normalized resource."""

    def __init__(self, policy: PolicyDefinition):
        self.policy = policy

    def applies_to(self, resource: ResourceModel) -> bool:
        return resource.resource_type in self.policy.resource_types

    def evaluate(self, resource: ResourceModel) -> RuleEvaluation:
        if not self.applies_to(resource):
            return RuleEvaluation(
                rule_id=self.policy.id,
                rule_name=self.policy.name,
                status="NOT_APPLICABLE",
                severity=self.policy.severity,
                message="Rule does not apply to this resource type.",
                field=self.policy.field,
                expected=self.policy.expected,
                actual=None,
            )

        missing = self.policy.field not in resource.configuration
        actual = resource.configuration.get(self.policy.field)
        passed = False if missing else self._compare(actual, self.policy.expected)

        return RuleEvaluation(
            rule_id=self.policy.id,
            rule_name=self.policy.name,
            status="PASS" if passed else "FAIL",
            severity=self.policy.severity,
            message=self.policy.message,
            field=self.policy.field,
            expected=self.policy.expected,
            actual=actual,
        )

    def _compare(self, actual: Any, expected: Any) -> bool:
        if self.policy.operator == "equals":
            return actual == expected
        if self.policy.operator == "not_equals":
            return actual != expected
        raise ValueError(f"Unsupported policy operator: {self.policy.operator}")


BaseRule = ConfigurableRule
EncryptionRequiredRule = ConfigurableRule
LoggingRequiredRule = ConfigurableRule
PublicExposureForbiddenRule = ConfigurableRule
