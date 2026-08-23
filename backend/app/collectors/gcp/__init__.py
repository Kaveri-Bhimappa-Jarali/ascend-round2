"""
GCP Collector module entrypoint.
"""
import os
import logging
from typing import List
from app.collectors.base import BaseCollector
from app.models.resource import ResourceModel
from app.collectors.gcp.client import GCPClient
from app.collectors.gcp.storage import StorageCollector
from app.collectors.gcp.cloud_sql import CloudSQLCollector
from app.collectors.gcp.vpc import VPCCollector

logger = logging.getLogger(__name__)

class GCPCollector(BaseCollector):
    """
    Unified GCP resource configuration scanner.
    Orchestrates GCS, Cloud SQL, and VPC scanning. Handles fallback to Demo mode.
    """
    def __init__(self, demo_mode: bool = None):
        if demo_mode is not None:
            self.demo_mode = demo_mode
        else:
            gcp_demo = os.environ.get("GCP_DEMO_MODE", "false").lower() == "true"
            # Application Default Credentials (ADC) usually uses GOOGLE_APPLICATION_CREDENTIALS 
            # or checks standard paths. We'll default to demo mode if explicitly asked or 
            # if GOOGLE_APPLICATION_CREDENTIALS environment variable is not defined.
            has_credentials = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS") is not None
            self.demo_mode = gcp_demo or not has_credentials

    def collect_resources(self) -> List[ResourceModel]:
        """
        Orchestrate resource scans. Returns list of normalized ResourceModel.
        """
        if self.demo_mode:
            logger.info("GCP Scan triggered in DEMO MODE. Returning mock/sample data.")
            return self._get_demo_resources()

        logger.info("GCP Scan triggered in PRODUCTION/REAL MODE.")
        client = GCPClient()
        resources = []

        # Gather GCS buckets
        storage_scanner = StorageCollector(gcp_client=client)
        resources.extend(storage_scanner.collect_resources())

        # Gather Cloud SQL instances
        sql_scanner = CloudSQLCollector(gcp_client=client)
        resources.extend(sql_scanner.collect_resources())

        # Gather VPC networks
        vpc_scanner = VPCCollector(gcp_client=client)
        resources.extend(vpc_scanner.collect_resources())

        return resources

    def _get_demo_resources(self) -> List[ResourceModel]:
        """
        Generates clearly labelled demo resources representing standard test cases.
        """
        return [
            # GCS Buckets
            ResourceModel(
                provider="GCP",
                resource_type="storage",
                resource_id="demo-gcp-storage-compliant",
                resource_name="demo-gcp-storage-compliant",
                configuration={
                    "encryption_enabled": True,
                    "public_access": False,
                    "logging_enabled": True,
                    "region": "us-central1",
                    "arn": "gs://demo-gcp-storage-compliant"
                }
            ),
            ResourceModel(
                provider="GCP",
                resource_type="storage",
                resource_id="demo-gcp-storage-public",
                resource_name="demo-gcp-storage-public",
                configuration={
                    "encryption_enabled": True,
                    "public_access": True,
                    "logging_enabled": False,
                    "region": "us-central1",
                    "arn": "gs://demo-gcp-storage-public"
                }
            ),
            # Cloud SQL Instances
            ResourceModel(
                provider="GCP",
                resource_type="database",
                resource_id="demo-gcp-sql-compliant",
                resource_name="demo-gcp-sql-compliant",
                configuration={
                    "encryption_enabled": True,
                    "public_access": False,
                    "logging_enabled": True,
                    "engine": "POSTGRES_14",
                    "region": "us-central1",
                    "arn": "gcp:sqladmin:us-central1:demo-project:instances:demo-gcp-sql-compliant"
                }
            ),
            ResourceModel(
                provider="GCP",
                resource_type="database",
                resource_id="demo-gcp-sql-public",
                resource_name="demo-gcp-sql-public",
                configuration={
                    "encryption_enabled": True,
                    "public_access": True,
                    "logging_enabled": False,
                    "engine": "MYSQL_8_0",
                    "region": "us-central1",
                    "arn": "gcp:sqladmin:us-central1:demo-project:instances:demo-gcp-sql-public"
                }
            ),
            # VPC Networks
            ResourceModel(
                provider="GCP",
                resource_type="vpc",
                resource_id="demo-gcp-vpc-default",
                resource_name="demo-gcp-vpc-default",
                configuration={
                    "routing_mode": "regional",
                    "auto_create_subnetworks": True,
                    "subnets_count": 4,
                    "region": "global",
                    "encryption_enabled": True,
                    "public_access": False,
                    "logging_enabled": True
                }
            )
        ]
