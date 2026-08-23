"""
CLI seeder utility to populate SQLite database with demo multi-cloud resources
and export a JSON compliance audit report.
"""

import argparse
from pathlib import Path
import sys

# Ensure backend directory is in Python path when executed directly
BACKEND_ROOT = Path(__file__).resolve().parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database.database import get_session, init_db
from app.database.models import ResourceDB, ViolationDB
from app.models.resource import ResourceModel
from app.services.compliance_service import ComplianceService


DEMO_RESOURCES = [
    # 1. AWS Compliant S3 Storage
    ResourceModel(
        provider="AWS",
        resource_type="storage",
        resource_id="demo-aws-s3-compliant",
        resource_name="aws-prod-data-bucket",
        configuration={
            "encryption_enabled": True,
            "logging_enabled": True,
            "public_access": False,
            "region": "us-east-1",
        },
    ),
    # 2. AWS Non-Compliant S3 Storage (Fails Encryption, Logging, Public Access)
    ResourceModel(
        provider="AWS",
        resource_type="storage",
        resource_id="demo-aws-s3-non-compliant",
        resource_name="aws-public-unencrypted-bucket",
        configuration={
            "encryption_enabled": False,
            "logging_enabled": False,
            "public_access": True,
            "region": "us-west-2",
        },
    ),
    # 3. AWS Non-Compliant RDS Database (Fails Encryption and Logging)
    ResourceModel(
        provider="AWS",
        resource_type="database",
        resource_id="demo-aws-rds-db",
        resource_name="aws-legacy-db-instance",
        configuration={
            "encryption_enabled": False,
            "logging_enabled": False,
            "public_access": False,
            "engine": "postgres",
        },
    ),
    # 4. GCP Compliant Storage Bucket
    ResourceModel(
        provider="GCP",
        resource_type="storage",
        resource_id="demo-gcp-storage-compliant",
        resource_name="gcp-secured-audit-logs",
        configuration={
            "encryption_enabled": True,
            "logging_enabled": True,
            "public_access": False,
            "location": "US",
        },
    ),
    # 5. GCP Non-Compliant Cloud SQL Database (Fails Encryption)
    ResourceModel(
        provider="GCP",
        resource_type="database",
        resource_id="demo-gcp-cloudsql-db",
        resource_name="gcp-dev-sql-instance",
        configuration={
            "encryption_enabled": False,
            "logging_enabled": True,
            "public_access": False,
            "database_version": "MYSQL_8_0",
        },
    ),
    # 6. GCP Non-Compliant VPC Network (Fails Public Access)
    ResourceModel(
        provider="GCP",
        resource_type="vpc",
        resource_id="demo-gcp-vpc-network",
        resource_name="gcp-default-vpc",
        configuration={
            "public_access": True,
            "logging_enabled": False,
            "auto_create_subnetworks": True,
        },
    ),
]


def seed_database(reset: bool = False, export_report: bool = True) -> dict:
    """Seed sample multi-cloud resources via ComplianceService."""

    init_db()
    session = next(get_session())

    try:
        if reset:
            print("[INFO] Clearing existing demo resources and violations (--reset-demo enabled)...")
            session.query(ViolationDB).delete()
            session.query(ResourceDB).delete()
            session.commit()

        service = ComplianceService(session)
        print(f"[INFO] Evaluating and seeding {len(DEMO_RESOURCES)} demo multi-cloud resources...")
        evaluations = service.evaluate_resources(DEMO_RESOURCES)

        summary = service.get_summary()
        print(f"[SUCCESS] Database seeded successfully!")
        print(f"  - Total Resources: {summary['total_resources']}")
        print(f"  - Compliant: {summary['compliant_resources']}")
        print(f"  - Non-Compliant: {summary['non_compliant_resources']}")
        print(f"  - Total Violations: {summary['total_violations']}")
        print(f"  - Compliance Percentage: {summary['compliance_percentage']}%")

        report = None
        if export_report:
            repo_root = BACKEND_ROOT.parent
            report_path = repo_root / "reports" / "generated" / "compliance_report.json"
            report = service.generate_json_report(output_path=report_path, environment="demo")
            print(f"[SUCCESS] JSON Compliance Report generated at: {report_path}")

        return summary
    finally:
        session.close()


def main():
    parser = argparse.ArgumentParser(description="Seed CloudCompliance Sentinel demo data into SQLite.")
    parser.add_argument(
        "--reset-demo",
        action="store_true",
        help="Explicitly clear existing resources and violations before seeding.",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Skip writing compliance_report.json file output.",
    )
    args = parser.parse_args()

    seed_database(reset=args.reset_demo, export_report=not args.no_report)


if __name__ == "__main__":
    main()
