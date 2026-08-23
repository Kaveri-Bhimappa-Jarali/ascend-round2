"""Database CRUD query abstractions for compliance data."""

from collections import Counter
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from app.compliance.rules import RuleEvaluation
from app.database.models import ResourceDB, ViolationDB
from app.models.resource import ResourceModel


class ComplianceRepository:
    """Handles read/write logic for resources and violations."""

    def __init__(self, session: Session):
        self.session = session

    def save_resource(self, resource: ResourceModel) -> ResourceDB:
        existing = (
            self.session.query(ResourceDB)
            .filter(
                ResourceDB.provider == resource.provider,
                ResourceDB.resource_type == resource.resource_type,
                ResourceDB.resource_id == resource.resource_id,
            )
            .one_or_none()
        )

        if existing is None:
            try:
                with self.session.begin_nested():
                    existing = ResourceDB(
                        provider=resource.provider,
                        resource_type=resource.resource_type,
                        resource_id=resource.resource_id,
                        resource_name=resource.resource_name,
                        configuration=resource.configuration,
                        last_seen=datetime.now(timezone.utc),
                    )
                    self.session.add(existing)
                    self.session.flush()
                    return existing
            except IntegrityError:
                existing = (
                    self.session.query(ResourceDB)
                    .filter(
                        ResourceDB.provider == resource.provider,
                        ResourceDB.resource_type == resource.resource_type,
                        ResourceDB.resource_id == resource.resource_id,
                    )
                    .one()
                )

        existing.resource_name = resource.resource_name
        existing.configuration = resource.configuration
        existing.last_seen = datetime.now(timezone.utc)
        self.session.flush()
        return existing


    def replace_violations(
        self,
        resource: ResourceDB,
        violations: Iterable[RuleEvaluation],
    ) -> list[ViolationDB]:
        self.session.query(ViolationDB).filter(ViolationDB.resource_db_id == resource.id).delete()

        saved: list[ViolationDB] = []
        for violation in violations:
            row = ViolationDB(
                resource_db_id=resource.id,
                resource_id=resource.resource_id,
                rule_id=violation.rule_id,
                severity=violation.severity.value,
                message=violation.message,
                status=violation.status,
                detected_at=datetime.now(timezone.utc),
            )
            self.session.add(row)
            saved.append(row)

        self.session.flush()
        return saved

    def list_resources(self) -> list[ResourceDB]:
        return self.session.query(ResourceDB).order_by(ResourceDB.provider, ResourceDB.resource_type).all()

    def list_violations(self) -> list[ViolationDB]:
        return (
            self.session.query(ViolationDB)
            .options(joinedload(ViolationDB.resource))
            .order_by(ViolationDB.detected_at.desc(), ViolationDB.id.desc())
            .all()
        )

    def get_compliance_statistics(self) -> dict[str, object]:
        total_resources = self.session.query(ResourceDB).count()
        failed_resource_ids = [
            row[0]
            for row in (
                self.session.query(ViolationDB.resource_db_id)
                .filter(ViolationDB.status == "FAIL")
                .distinct()
                .all()
            )
        ]
        non_compliant_resources = len(failed_resource_ids)
        compliant_resources = max(total_resources - non_compliant_resources, 0)
        total_violations = self.session.query(ViolationDB).filter(ViolationDB.status == "FAIL").count()

        severity_rows = (
            self.session.query(ViolationDB.severity, func.count(ViolationDB.id))
            .filter(ViolationDB.status == "FAIL")
            .group_by(ViolationDB.severity)
            .all()
        )
        severity_counts = Counter({severity: count for severity, count in severity_rows})
        violations_by_severity = {
            "CRITICAL": severity_counts.get("CRITICAL", 0),
            "HIGH": severity_counts.get("HIGH", 0),
            "MEDIUM": severity_counts.get("MEDIUM", 0),
            "LOW": severity_counts.get("LOW", 0),
        }

        compliance_percentage = (
            round((compliant_resources / total_resources) * 100, 2)
            if total_resources
            else 100.0
        )

        return {
            "total_resources": total_resources,
            "compliant_resources": compliant_resources,
            "non_compliant_resources": non_compliant_resources,
            "total_violations": total_violations,
            "violations_by_severity": violations_by_severity,
            "compliance_percentage": compliance_percentage,
        }

    def get_full_report_data(self) -> dict[str, object]:
        summary = self.get_compliance_statistics()
        resources = self.list_resources()
        violations = self.list_violations()

        resource_data = []
        for res in resources:
            res_violations = [v for v in res.violations if v.status == "FAIL"]
            status = "NON_COMPLIANT" if res_violations else "COMPLIANT"
            resource_data.append({
                "provider": res.provider,
                "resource_type": res.resource_type,
                "resource_id": res.resource_id,
                "resource_name": res.resource_name,
                "status": status,
                "configuration": res.configuration,
                "last_seen": res.last_seen.isoformat() if res.last_seen else None,
            })

        violation_data = []
        for v in violations:
            violation_data.append({
                "provider": v.resource.provider if v.resource else "UNKNOWN",
                "resource_type": v.resource.resource_type if v.resource else "UNKNOWN",
                "resource_id": v.resource_id,
                "resource_name": v.resource.resource_name if v.resource else v.resource_id,
                "rule_id": v.rule_id,
                "severity": v.severity,
                "message": v.message,
                "status": v.status,
                "detected_at": v.detected_at.isoformat() if v.detected_at else None,
            })

        return {
            "summary": summary,
            "resources": resource_data,
            "violations": violation_data,
        }

