"""
GCP VPC resource configuration collector.
"""
import logging
from googleapiclient.errors import HttpError
from app.collectors.base import BaseCollector
from app.collectors.gcp.client import GCPClient
from app.models.resource import ResourceModel

logger = logging.getLogger(__name__)

class VPCCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of GCP VPC networks.
    """
    def __init__(self, gcp_client: GCPClient = None):
        self.gcp_client = gcp_client or GCPClient()

    def collect_resources(self) -> list[ResourceModel]:
        """
        Scan all GCP VPC networks and return their configurations normalized.
        """
        normalized_resources = []
        try:
            compute_service = self.gcp_client.get_compute_service()
            request = compute_service.networks().list(project=self.gcp_client.project_id)
            response = request.execute()
            networks = response.get("items", [])
        except HttpError as e:
            logger.error(f"Failed to list GCP VPC networks via Discovery API: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing GCP VPC networks: {e}")
            return []

        for network in networks:
            network_id = str(network.get("id", ""))
            network_name = network.get("name")
            if not network_name:
                continue

            try:
                routing_mode = "regional"
                routing_config = network.get("routingConfig", {})
                if routing_config and routing_config.get("routingMode"):
                    routing_mode = routing_config.get("routingMode").lower()

                auto_create = network.get("autoCreateSubnetworks", False)
                subnets = network.get("subnetworks", [])
                subnets_count = len(subnets) if subnets else 0

                normalized_resources.append(
                    ResourceModel(
                        provider="GCP",
                        resource_type="vpc",
                        resource_id=network_id or network_name,
                        resource_name=network_name,
                        configuration={
                            "routing_mode": routing_mode,
                            "auto_create_subnetworks": auto_create,
                            "subnets_count": subnets_count,
                            "region": "global",
                            "encryption_enabled": True,  # VPC doesn't apply encryption-at-rest directly
                            "public_access": False,       # Private by default
                            "logging_enabled": True       # Flow logs check can override this later
                        }
                    )
                )
            except Exception as vpc_err:
                logger.error(f"Failed to scan configuration for GCP VPC {network_name}: {vpc_err}", exc_info=True)
                # Continue scanning other networks

        return normalized_resources
