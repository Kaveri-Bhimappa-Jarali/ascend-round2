"""
GCP Cloud SQL resource configuration collector.
"""
from app.collectors.base import BaseCollector

class CloudSQLCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of GCP Cloud SQL instances.
    """
    def collect_resources(self):
        return []
