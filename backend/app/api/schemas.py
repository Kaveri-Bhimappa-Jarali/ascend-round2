"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ResourceInput(BaseModel):
    provider: str
    resource_type: str
    resource_id: str
    resource_name: str
    configuration: dict[str, Any]


class ViolationResponse(BaseModel):
    provider: str
    resource_type: str
    resource_id: str
    resource_name: str
    rule_id: str
    severity: str
    message: str
    status: str
    detected_at: datetime | None = None


class ResourceEvaluationResponse(BaseModel):
    provider: str
    resource_type: str
    resource_id: str
    resource_name: str
    status: str
    violations: list[ViolationResponse]


class ComplianceSummaryResponse(BaseModel):
    total_resources: int
    compliant_resources: int
    non_compliant_resources: int
    total_violations: int
    violations_by_severity: dict[str, int]
    compliance_percentage: float


class ReportMetadataSchema(BaseModel):
    report_id: str
    schema_version: str
    generated_at: str
    environment: str


class JSONReportResponse(BaseModel):
    metadata: ReportMetadataSchema
    summary: ComplianceSummaryResponse
    resources: list[dict[str, Any]]
    violations: list[dict[str, Any]]


class ResourceDBResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    provider: str
    resource_type: str
    resource_id: str
    resource_name: str
    configuration: dict[str, Any]
