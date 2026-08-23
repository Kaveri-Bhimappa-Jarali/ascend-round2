"""
Compliance report generator module for JSON audit reports.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any
import uuid


class JSONReportGenerator:
    """Generates structured JSON compliance reports from repository data."""

    DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "generated"

    def build_report(
        self,
        report_data: dict[str, Any],
        environment: str = "production",
    ) -> dict[str, Any]:
        """Compile a deterministic JSON report structure."""

        report_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc).isoformat()

        summary = report_data.get("summary", {})
        resources = report_data.get("resources", [])
        violations = report_data.get("violations", [])

        return {
            "metadata": {
                "report_id": report_id,
                "schema_version": "1.0.0",
                "generated_at": generated_at,
                "environment": environment,
            },
            "summary": {
                "total_resources": summary.get("total_resources", 0),
                "compliant_resources": summary.get("compliant_resources", 0),
                "non_compliant_resources": summary.get("non_compliant_resources", 0),
                "total_violations": summary.get("total_violations", 0),
                "compliance_percentage": summary.get("compliance_percentage", 100.0),
                "violations_by_severity": summary.get("violations_by_severity", {
                    "CRITICAL": 0,
                    "HIGH": 0,
                    "MEDIUM": 0,
                    "LOW": 0,
                }),
            },
            "resources": resources,
            "violations": violations,
        }

    def export_json(
        self,
        report_dict: dict[str, Any],
        output_path: Path | str | None = None,
    ) -> Path:
        """Write the report structure to disk as formatted JSON."""

        if output_path is None:
            output_dir = self.DEFAULT_OUTPUT_DIR
            output_dir.mkdir(parents=True, exist_ok=True)
            target = output_dir / "compliance_report.json"
        else:
            target = Path(output_path)
            target.parent.mkdir(parents=True, exist_ok=True)

        target.write_text(json.dumps(report_dict, indent=2), encoding="utf-8")
        return target


# Maintain backwards compatibility
ReportGenerator = JSONReportGenerator
