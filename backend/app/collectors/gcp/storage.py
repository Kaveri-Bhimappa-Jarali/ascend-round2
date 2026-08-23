"""
GCP Cloud Storage resource configuration collector.
"""
import logging
from google.api_core.exceptions import GoogleAPIError
from app.collectors.base import BaseCollector
from app.collectors.gcp.client import GCPClient
from app.models.resource import ResourceModel

logger = logging.getLogger(__name__)

class StorageCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of GCP Storage Buckets.
    """
    def __init__(self, gcp_client: GCPClient = None):
        self.gcp_client = gcp_client or GCPClient()

    def collect_resources(self) -> list[ResourceModel]:
        """
        Scan all GCS buckets and return their configurations normalized.
        """
        normalized_resources = []
        try:
            storage_client = self.gcp_client.get_storage_client()
            buckets = list(storage_client.list_buckets())
        except GoogleAPIError as e:
            logger.error(f"Failed to list GCP Storage buckets: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing GCP Storage buckets: {e}")
            return []

        for bucket in buckets:
            bucket_name = bucket.name
            try:
                # 1. Region
                region = bucket.location.lower() if bucket.location else "us"

                # 2. Encryption
                # GCS is always encrypted-at-rest. If CMEK is set, it uses KMS.
                # For basic compliance, we report True because Google always encrypts at rest.
                encryption_enabled = True

                # 3. Public Access Checking
                public_access = True
                iam_config = getattr(bucket, "iam_configuration", None)
                public_access_prevention = None
                if iam_config and hasattr(iam_config, "public_access_prevention"):
                    public_access_prevention = iam_config.public_access_prevention

                if public_access_prevention == "enforced":
                    public_access = False
                else:
                    # Fallback: check IAM policy bindings for allUsers or allAuthenticatedUsers
                    try:
                        policy = bucket.get_iam_policy()
                        has_public_binding = False
                        for binding in policy.bindings:
                            members = binding.get("members", [])
                            if "allUsers" in members or "allAuthenticatedUsers" in members:
                                has_public_binding = True
                                break
                        if not has_public_binding:
                            public_access = False
                    except Exception as iam_err:
                        logger.warning(f"Could not fetch IAM policy for GCS bucket {bucket_name}: {iam_err}")
                        # Keep conservative security posture: assume public/unblocked if check fails

                # 4. Logging configuration
                logging_enabled = False
                bucket_logging = getattr(bucket, "logging", None)
                if bucket_logging and isinstance(bucket_logging, dict) and bucket_logging.get("logBucket"):
                    logging_enabled = True

                # Build Normalized Resource Model
                resource_arn = f"gs://{bucket_name}"
                normalized_resources.append(
                    ResourceModel(
                        provider="GCP",
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
                logger.error(f"Failed to scan configuration for GCP bucket {bucket_name}: {bucket_err}", exc_info=True)
                # Continue scanning other buckets

        return normalized_resources
