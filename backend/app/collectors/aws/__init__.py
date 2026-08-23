"""
AWS Collector module entrypoint.
"""
import os
import logging
from typing import List
from app.collectors.base import BaseCollector
from app.models.resource import ResourceModel
from app.collectors.aws.client import AWSClient
from app.collectors.aws.s3 import S3Collector
from app.collectors.aws.rds import RDSCollector
from app.collectors.aws.vpc import VPCCollector

logger = logging.getLogger(__name__)

class AWSCollector(BaseCollector):
    """
    Unified AWS resource configuration scanner.
    Orchestrates S3, RDS, and VPC scanning. Handles fallback to Demo mode.
    """
    def __init__(self, demo_mode: bool = None):
        if demo_mode is not None:
            self.demo_mode = demo_mode
        else:
            aws_demo = os.environ.get("AWS_DEMO_MODE", "false").lower() == "true"
            has_credentials = (
                os.environ.get("AWS_ACCESS_KEY_ID") is not None and 
                os.environ.get("AWS_SECRET_ACCESS_KEY") is not None
            )
            # Default to demo mode if explicitly set, or if no credentials exist
            self.demo_mode = aws_demo or not has_credentials

    def collect_resources(self) -> List[ResourceModel]:
        """
        Orchestrate resource scans. Returns list of normalized ResourceModel.
        """
        if self.demo_mode:
            logger.info("AWS Scan triggered in DEMO MODE. Returning mock/sample data.")
            return self._get_demo_resources()

        logger.info("AWS Scan triggered in PRODUCTION/REAL MODE.")
        client = AWSClient()
        resources = []

        # Gather S3 buckets
        s3_scanner = S3Collector(aws_client=client)
        resources.extend(s3_scanner.collect_resources())

        # Gather RDS DB instances
        rds_scanner = RDSCollector(aws_client=client)
        resources.extend(rds_scanner.collect_resources())

        # Gather VPC configurations
        vpc_scanner = VPCCollector(aws_client=client)
        resources.extend(vpc_scanner.collect_resources())

        return resources

    def _get_demo_resources(self) -> List[ResourceModel]:
        """
        Generates clearly labelled demo resources representing standard test cases.
        """
        return [
            # S3 Buckets
            ResourceModel(
                provider="AWS",
                resource_type="storage",
                resource_id="demo-aws-s3-compliant",
                resource_name="demo-aws-s3-compliant",
                configuration={
                    "encryption_enabled": True,
                    "public_access": False,
                    "logging_enabled": True,
                    "region": "us-east-1",
                    "arn": "arn:aws:s3:::demo-aws-s3-compliant"
                }
            ),
            ResourceModel(
                provider="AWS",
                resource_type="storage",
                resource_id="demo-aws-s3-unencrypted",
                resource_name="demo-aws-s3-unencrypted",
                configuration={
                    "encryption_enabled": False,
                    "public_access": False,
                    "logging_enabled": True,
                    "region": "us-east-1",
                    "arn": "arn:aws:s3:::demo-aws-s3-unencrypted"
                }
            ),
            ResourceModel(
                provider="AWS",
                resource_type="storage",
                resource_id="demo-aws-s3-public",
                resource_name="demo-aws-s3-public",
                configuration={
                    "encryption_enabled": True,
                    "public_access": True,
                    "logging_enabled": True,
                    "region": "us-east-1",
                    "arn": "arn:aws:s3:::demo-aws-s3-public"
                }
            ),
            # RDS Databases
            ResourceModel(
                provider="AWS",
                resource_type="database",
                resource_id="demo-aws-rds-compliant",
                resource_name="demo-aws-rds-compliant",
                configuration={
                    "encryption_enabled": True,
                    "public_access": False,
                    "logging_enabled": True,
                    "engine": "postgres",
                    "engine_version": "14.5",
                    "region": "us-east-1",
                    "arn": "arn:aws:rds:us-east-1:123456789012:db:demo-aws-rds-compliant"
                }
            ),
            ResourceModel(
                provider="AWS",
                resource_type="database",
                resource_id="demo-aws-rds-public",
                resource_name="demo-aws-rds-public",
                configuration={
                    "encryption_enabled": True,
                    "public_access": True,
                    "logging_enabled": False,
                    "engine": "mysql",
                    "engine_version": "8.0",
                    "region": "us-east-1",
                    "arn": "arn:aws:rds:us-east-1:123456789012:db:demo-aws-rds-public"
                }
            ),
            # VPC Networks
            ResourceModel(
                provider="AWS",
                resource_type="vpc",
                resource_id="demo-aws-vpc-default",
                resource_name="demo-aws-vpc-default",
                configuration={
                    "cidr_block": "172.31.0.0/16",
                    "is_default": True,
                    "state": "available",
                    "region": "us-east-1",
                    "encryption_enabled": True,
                    "public_access": False,
                    "logging_enabled": True
                }
            )
        ]
