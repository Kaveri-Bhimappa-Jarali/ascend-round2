"""
AWS RDS resource configuration collector.
"""
import logging
from botocore.exceptions import ClientError
from app.collectors.base import BaseCollector
from app.collectors.aws.client import AWSClient
from app.models.resource import ResourceModel

logger = logging.getLogger(__name__)

class RDSCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of RDS database instances.
    """
    def __init__(self, aws_client: AWSClient = None):
        self.aws_client = aws_client or AWSClient()

    def collect_resources(self) -> list[ResourceModel]:
        """
        Scan all RDS database instances and return their configurations normalized.
        """
        normalized_resources = []
        try:
            rds_client = self.aws_client.get_rds_client()
            response = rds_client.describe_db_instances()
        except ClientError as e:
            logger.error(f"Failed to describe RDS instances: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error describing RDS instances: {e}")
            return []

        db_instances = response.get("DBInstances", [])
        for db in db_instances:
            db_id = db.get("DBInstanceIdentifier")
            if not db_id:
                continue

            try:
                arn = db.get("DBInstanceArn", "")
                
                # Extract region from ARN if present, e.g., arn:aws:rds:us-east-1:123456789012:db:instance-id
                region = self.aws_client.region_name or "us-east-1"
                if arn and len(arn.split(":")) > 3:
                    region = arn.split(":")[3]

                encryption_enabled = db.get("StorageEncrypted", False)
                public_access = db.get("PubliclyAccessible", False)
                
                # Check if CloudWatch log exports are configured
                log_exports = db.get("EnabledCloudwatchLogsExports", [])
                logging_enabled = len(log_exports) > 0

                engine = db.get("Engine", "")
                engine_version = db.get("EngineVersion", "")

                normalized_resources.append(
                    ResourceModel(
                        provider="AWS",
                        resource_type="database",
                        resource_id=db_id,
                        resource_name=db_id,
                        configuration={
                            "encryption_enabled": encryption_enabled,
                            "public_access": public_access,
                            "logging_enabled": logging_enabled,
                            "engine": engine,
                            "engine_version": engine_version,
                            "region": region,
                            "arn": arn
                        }
                    )
                )
            except Exception as db_err:
                logger.error(f"Failed to scan configuration for RDS instance {db_id}: {db_err}", exc_info=True)
                # Continue scanning other RDS instances

        return normalized_resources
