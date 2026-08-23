"""
GCP client session and credential helper.
"""
import os
import logging
from google.cloud import storage
from googleapiclient import discovery

logger = logging.getLogger(__name__)

class GCPClient:
    """
    Manages centralized GCP clients using discovery API for SQL Admin and Compute services.
    """
    project_id: str = None

    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.environ.get("GCP_PROJECT") or os.environ.get("GCP_DEFAULT_PROJECT", "cloudcompliance-sentinel-demo")

    def get_storage_client(self) -> storage.Client:
        """
        Returns an initialized Google Cloud Storage Client.
        """
        try:
            return storage.Client(project=self.project_id)
        except Exception as e:
            logger.error(f"Failed to initialize Google Storage Client: {e}")
            raise e

    def get_sql_service(self):
        """
        Returns an initialized SQL Admin discovery service.
        """
        try:
            return discovery.build('sqladmin', 'v1')
        except Exception as e:
            logger.error(f"Failed to initialize SQL Admin Service: {e}")
            raise e

    def get_compute_service(self):
        """
        Returns an initialized Compute discovery service.
        """
        try:
            return discovery.build('compute', 'v1')
        except Exception as e:
            logger.error(f"Failed to initialize Compute Service: {e}")
            raise e
