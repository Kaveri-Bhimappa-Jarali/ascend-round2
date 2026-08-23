"""API endpoint definitions."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import (
    ComplianceSummaryResponse,
    ResourceEvaluationResponse,
    ResourceInput,
    ViolationResponse,
)
from app.database.database import get_session
from app.database.models import ViolationDB
from app.models.resource import ResourceModel
from app.services.compliance_service import ComplianceService

router = APIRouter(prefix="/api")


def _violation_to_response(violation: ViolationDB) -> ViolationResponse:
    return ViolationResponse(
        provider=violation.resource.provider,
        resource_type=violation.resource.resource_type,
        resource_id=violation.resource.resource_id,
        resource_name=violation.resource.resource_name,
        rule_id=violation.rule_id,
        severity=violation.severity,
        message=violation.message,
        status=violation.status,
        detected_at=violation.detected_at,
    )


@router.post("/resources/evaluate", response_model=list[ResourceEvaluationResponse])
def evaluate_resources(
    resources: list[ResourceInput],
    session: Session = Depends(get_session),
) -> list[ResourceEvaluationResponse]:
    """Evaluate resource configurations against active compliance policies."""

    service = ComplianceService(session)
    seen = set()
    unique_models = []
    for resource in resources:
        key = (resource.provider, resource.resource_type, resource.resource_id)
        if key not in seen:
            seen.add(key)
            unique_models.append(ResourceModel(**resource.model_dump()))
    evaluations = service.evaluate_resources(unique_models)


    return [
        ResourceEvaluationResponse(
            provider=evaluation.resource.provider,
            resource_type=evaluation.resource.resource_type,
            resource_id=evaluation.resource.resource_id,
            resource_name=evaluation.resource.resource_name,
            status=evaluation.status,
            violations=[
                ViolationResponse(
                    provider=evaluation.resource.provider,
                    resource_type=evaluation.resource.resource_type,
                    resource_id=evaluation.resource.resource_id,
                    resource_name=evaluation.resource.resource_name,
                    rule_id=violation.rule_id,
                    severity=violation.severity.value,
                    message=violation.message,
                    status=violation.status,
                    detected_at=None,
                )
                for violation in evaluation.violations
            ],
        )
        for evaluation in evaluations
    ]


@router.get("/violations", response_model=list[ViolationResponse])
def get_violations(session: Session = Depends(get_session)) -> list[ViolationResponse]:
    """Retrieve compliance violations detected in the cloud environment."""

    service = ComplianceService(session)
    return [_violation_to_response(violation) for violation in service.get_violations()]


@router.get("/compliance/summary", response_model=ComplianceSummaryResponse)
def get_compliance_summary(session: Session = Depends(get_session)) -> dict[str, object]:
    """Calculate and return compliance percentages and severity metrics."""

    service = ComplianceService(session)
    return service.get_summary()

