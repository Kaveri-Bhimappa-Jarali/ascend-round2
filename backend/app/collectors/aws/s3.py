"""
AWS S3 resource configuration collector.
"""
import logging
from botocore.exceptions import ClientError
from app.collectors.base import BaseCollector
from app.collectors.aws.client import AWSClient
from app.models.resource import ResourceModel

logger = logging.getLogger(__name__)

class S3Collector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of S3 buckets.
    """
    def __init__(self, aws_client: AWSClient = None):
        self.aws_client = aws_client or AWSClient()

    def collect_resources(self) -> list[ResourceModel]:
        """
        Scan all S3 buckets and return their configurations normalized.
        """
        normalized_resources = []
        try:
            s3_client = self.aws_client.get_s3_client()
            response = s3_client.list_buckets()
        except ClientError as e:
            logger.error(f"Failed to list S3 buckets: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing S3 buckets: {e}")
            return []

        buckets = response.get("Buckets", [])
        for bucket in buckets:
            bucket_name = bucket.get("Name")
            if not bucket_name:
                continue

            try:
                # 1. Detect Bucket Region
                try:
                    loc_resp = s3_client.get_bucket_location(Bucket=bucket_name)
                    region = loc_resp.get("LocationConstraint")
                    # If LocationConstraint is None or empty, the bucket is in us-east-1
                    if not region:
                        region = "us-east-1"
                    elif region == "EU":
                        region = "eu-west-1"
                except ClientError as loc_err:
                    logger.warning(f"Could not get location for bucket {bucket_name}: {loc_err}")
                    region = self.aws_client.region_name or "us-east-1"

                # 2. Check Encryption status
                encryption_enabled = False
                try:
                    s3_client.get_bucket_encryption(Bucket=bucket_name)
                    encryption_enabled = True
                except ClientError as enc_err:
                    err_code = enc_err.response.get("Error", {}).get("Code")
                    if err_code != "ServerSideEncryptionConfigurationNotFoundError":
                        logger.warning(f"Error checking encryption for bucket {bucket_name}: {enc_err}")

                # 3. Check Public Access Block
                public_access = True
                try:
                    pab_resp = s3_client.get_public_access_block(Bucket=bucket_name)
                    pab_config = pab_resp.get("PublicAccessBlockConfiguration", {})
                    # If all blocks are True, then it is NOT publicly exposed
                    block_acls = pab_config.get("BlockPublicAcls", False)
                    ignore_acls = pab_config.get("IgnorePublicAcls", False)
                    block_policy = pab_config.get("BlockPublicPolicy", False)
                    restrict_buckets = pab_config.get("RestrictPublicBuckets", False)
                    
                    if block_acls and ignore_acls and block_policy and restrict_buckets:
                        public_access = False
                except ClientError as pab_err:
                    err_code = pab_err.response.get("Error", {}).get("Code")
                    if err_code == "NoSuchPublicAccessBlockConfiguration":
                        # Public Access Block not configured, bucket could be public
                        public_access = True
                    else:
                        logger.warning(f"Error checking public access block for bucket {bucket_name}: {pab_err}")
                        # Keep conservative security posture: assume public if check failed

                # 4. Check Logging configuration
                logging_enabled = False
                try:
                    log_resp = s3_client.get_bucket_logging(Bucket=bucket_name)
                    if "LoggingEnabled" in log_resp:
                        logging_enabled = True
                except ClientError as log_err:
                    logger.warning(f"Error checking logging configuration for bucket {bucket_name}: {log_err}")

                # Build Normalized Resource Model
                resource_arn = f"arn:aws:s3:::{bucket_name}"
                normalized_resources.append(
                    ResourceModel(
                        provider="AWS",
                        resource_type="storage",
                        resource_id=bucket_name,
                        resource_name=bucket_name,
                        configuration={
                            "encryption_enabled": encryption_enabled,
                            "public_access": public_access,
                            "logging_enabled": logging_enabled,
                            "region": region,
                            "arn": resource_arn
                        }
                    )
                )
            except Exception as bucket_err:
                logger.error(f"Failed to scan configuration for bucket {bucket_name}: {bucket_err}", exc_info=True)
                # Continue scanning other buckets

        return normalized_resources
