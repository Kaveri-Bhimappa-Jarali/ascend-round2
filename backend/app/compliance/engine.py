"""Provider-agnostic compliance engine."""

from dataclasses import dataclass

from app.compliance.policies import PolicyDefinition, load_policies
from app.compliance.rules import ConfigurableRule, RuleEvaluation
from app.models.resource import ResourceModel


@dataclass(frozen=True)
class ResourceEvaluation:
    resource: ResourceModel
    status: str
    rule_results: list[RuleEvaluation]
    violations: list[RuleEvaluation]


class ComplianceEngine:
    """Orchestrates policy selection and rule execution for normalized resources."""

    def __init__(self, policies: list[PolicyDefinition] | None = None):
        self.policies = policies if policies is not None else load_policies()
        self.rules = [ConfigurableRule(policy) for policy in self.policies]

    def evaluate(self, resource: ResourceModel) -> ResourceEvaluation:
        applicable_results = [
            rule.evaluate(resource)
            for rule in self.rules
            if rule.applies_to(resource)
        ]
        violations = [result for result in applicable_results if result.status == "FAIL"]
        status = "NON_COMPLIANT" if violations else "COMPLIANT"

        return ResourceEvaluation(
            resource=resource,
            status=status,
            rule_results=applicable_results,
            violations=violations,
        )

    def evaluate_many(self, resources: list[ResourceModel]) -> list[ResourceEvaluation]:
        return [self.evaluate(resource) for resource in resources]
