from datetime import datetime, timezone

from fastapi import APIRouter

from app.db.database import get_session
from app.db.models import ResourceSnapshot, Violation

router = APIRouter()


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "cloud-compliance-sentinel"}


@router.get("/summary")
async def summary() -> dict[str, object]:
    with get_session() as session:
        total_resources = session.query(ResourceSnapshot).count()
        violations = session.query(Violation).filter(Violation.status == "FAIL").count()

    compliant_resources = max(total_resources - violations, 0)
    compliance_score = (
        round((compliant_resources / total_resources) * 100, 2)
        if total_resources
        else 100.0
    )

    return {
        "total_resources": total_resources,
        "compliant_resources": compliant_resources,
        "violations": violations,
        "compliance_score": compliance_score,
        "score_label": "Internal compliance score, not an official certification score",
        "last_scan": None,
        "severity": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
    }


@router.get("/resources")
async def resources() -> list[dict[str, object]]:
    with get_session() as session:
        rows = session.query(ResourceSnapshot).order_by(ResourceSnapshot.provider).all()
        return [row.to_dict() for row in rows]


@router.get("/violations")
async def violations() -> list[dict[str, object]]:
    with get_session() as session:
        rows = session.query(Violation).order_by(Violation.detected_at.desc()).all()
        return [row.to_dict() for row in rows]


@router.get("/providers")
async def providers() -> dict[str, dict[str, object]]:
    return {
        "aws": {"resources": 0, "violations": 0, "status": "Not scanned"},
        "gcp": {"resources": 0, "violations": 0, "status": "Not scanned"},
    }


@router.post("/scan")
async def scan() -> dict[str, object]:
    return {
        "status": "accepted",
        "message": "Scan pipeline is scheduled for Phase 4",
        "started_at": _utc_now(),
    }
