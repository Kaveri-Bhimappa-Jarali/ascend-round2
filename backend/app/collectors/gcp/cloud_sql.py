"""
GCP Cloud SQL resource configuration collector.
"""
import logging
from googleapiclient.errors import HttpError
from app.collectors.base import BaseCollector
from app.collectors.gcp.client import GCPClient
from app.models.resource import ResourceModel

logger = logging.getLogger(__name__)

class CloudSQLCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of GCP Cloud SQL instances.
    """
    def __init__(self, gcp_client: GCPClient = None):
        self.gcp_client = gcp_client or GCPClient()

    def collect_resources(self) -> list[ResourceModel]:
        """
        Scan all GCP Cloud SQL instances and return their configurations normalized.
        """
        normalized_resources = []
        try:
            sql_service = self.gcp_client.get_sql_service()
            request = sql_service.instances().list(project=self.gcp_client.project_id)
            response = request.execute()
            instances = response.get("items", [])
        except HttpError as e:
            logger.error(f"Failed to list GCP Cloud SQL instances via Discovery API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing GCP Cloud SQL instances: {e}")
            return []

        for instance in instances:
            instance_name = instance.get("name")
            if not instance_name:
                continue

            try:
                # 1. Engine & Region
                engine = instance.get("databaseVersion", "")
                region = instance.get("region", "us-central1")

                # 2. Encryption
                # Cloud SQL is always encrypted-at-rest by default.
                encryption_enabled = True

                # 3. Public access (IPv4 external network enabled)
                public_access = False
                settings = instance.get("settings", {})
                ip_config = settings.get("ipConfiguration", {})
                if ip_config:
                    # ipv4Enabled can be a boolean or a string depending on serialization
                    ipv4 = ip_config.get("ipv4Enabled")
                    if isinstance(ipv4, str):
                        public_access = ipv4.lower() == "true"
                    else:
                        public_access = bool(ipv4)

                # 4. Logging Check (Check if logging database flags are enabled)
                logging_enabled = False
                db_flags = settings.get("databaseFlags", [])
                if db_flags:
                    for flag in db_flags:
                        name = flag.get("name")
                        value = flag.get("value")
                        # Common logging flags for postgres and mysql
                        if name in ["log_connections", "log_disconnections", "general_log", "log_statement"] and str(value).lower() in ["on", "all", "true"]:
                            logging_enabled = True
                            break

                # Build Normalized Resource Model
                resource_arn = f"gcp:sqladmin:{region}:{self.gcp_client.project_id}:instances:{instance_name}"
                normalized_resources.append(
                    ResourceModel(
                        provider="GCP",
                        resource_type="database",
                        resource_id=instance_name,
                        resource_name=instance_name,
                        configuration={
                            "encryption_enabled": encryption_enabled,
                            "public_access": public_access,
                            "logging_enabled": logging_enabled,
                            "engine": engine,
                            "region": region,
                            "arn": resource_arn
                        }
                    )
                )
            except Exception as sql_err:
                logger.error(f"Failed to scan configuration for GCP SQL instance {instance_name}: {sql_err}", exc_info=True)
                # Continue scanning other Cloud SQL instances

        return normalized_resources
