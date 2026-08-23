"""Policy loading and validation for configurable compliance rules."""

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from app.compliance.severity import Severity

SUPPORTED_OPERATORS = {"equals", "not_equals"}
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[2] / "policies" / "policies.json"


class PolicyDefinition(BaseModel):
    id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    resource_types: list[str] = Field(min_length=1)
    field: str = Field(min_length=1)
    operator: Literal["equals", "not_equals"]
    expected: Any
    severity: Severity
    message: str = Field(min_length=1)


class PolicySet(BaseModel):
    rules: list[PolicyDefinition]


def load_policies(path: Path | str = DEFAULT_POLICY_PATH) -> list[PolicyDefinition]:
    policy_path = Path(path)
    try:
        raw = policy_path.read_text(encoding="utf-8")
        policy_set = PolicySet.model_validate_json(raw)
    except FileNotFoundError as exc:
        raise ValueError(f"Policy file not found: {policy_path}") from exc
    except ValidationError as exc:
        raise ValueError(f"Invalid policy configuration: {exc}") from exc

    invalid = [rule.operator for rule in policy_set.rules if rule.operator not in SUPPORTED_OPERATORS]
    if invalid:
        raise ValueError(f"Unsupported policy operator(s): {', '.join(sorted(set(invalid)))}")

    rule_ids = [rule.id for rule in policy_set.rules]
    if len(rule_ids) != len(set(rule_ids)):
        raise ValueError("Duplicate policy rule IDs found in configuration.")

    return policy_set.rules

