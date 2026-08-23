"""Compliance service layer linking API calls, engine evaluations, and database writes."""

from sqlalchemy.orm import Session

from app.compliance.engine import ComplianceEngine, ResourceEvaluation
from app.database.repository import ComplianceRepository
from app.models.resource import ResourceModel


class ComplianceService:
    """Coordinates normalized resource evaluation and persistence."""

    def __init__(
        self,
        session: Session,
        engine: ComplianceEngine | None = None,
    ):
        self.repository = ComplianceRepository(session)
        self.engine = engine or ComplianceEngine()
        self.session = session

    def evaluate_resources(self, resources: list[ResourceModel]) -> list[ResourceEvaluation]:
        evaluations = self.engine.evaluate_many(resources)
        for evaluation in evaluations:
            resource_row = self.repository.save_resource(evaluation.resource)
            self.repository.replace_violations(resource_row, evaluation.violations)

        self.session.commit()
        return evaluations

    def get_violations(self):
        return self.repository.list_violations()

    def get_summary(self) -> dict[str, object]:
        return self.repository.get_compliance_statistics()
