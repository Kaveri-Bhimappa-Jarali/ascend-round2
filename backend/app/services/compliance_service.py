"""Compliance service layer linking API calls, engine evaluations, and database writes."""

from pathlib import Path
import sys
from typing import Any
from sqlalchemy.orm import Session

# Ensure repo root is available in sys.path for importing reports module
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from app.compliance.engine import ComplianceEngine, ResourceEvaluation
from app.database.repository import ComplianceRepository
from app.models.resource import ResourceModel
from reports.report_generator import JSONReportGenerator


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
        self.report_generator = JSONReportGenerator()

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

    def generate_json_report(
        self,
        output_path: Path | str | None = None,
        environment: str = "production",
    ) -> dict[str, Any]:
        report_data = self.repository.get_full_report_data()
        report_dict = self.report_generator.build_report(report_data, environment=environment)
        if output_path:
            self.report_generator.export_json(report_dict, output_path)
        return report_dict

    def generate_pdf_report(
        self,
        output_path: Path | str | None = None,
        environment: str = "production",
    ) -> Path:
        from reports.report_generator import PDFReportGenerator
        report_data = self.repository.get_full_report_data()
        report_dict = self.report_generator.build_report(report_data, environment=environment)
        pdf_gen = PDFReportGenerator()
        return pdf_gen.export_pdf(report_dict, output_path)
