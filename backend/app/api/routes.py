"""
API endpoint definitions.
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api")

@router.post("/resources/evaluate")
def evaluate_resources():
    """
    Evaluate resource configurations against active compliance policies.
    """
    return {"message": "Evaluate endpoint stub"}

@router.get("/violations")
def get_violations():
    """
    Retrieve compliance violations detected in the cloud environment.
    """
    return {"violations": []}

@router.get("/compliance/summary")
def get_compliance_summary():
    """
    Calculate and return compliance percentages and severity metrics.
    """
    return {"total_resources": 0}
