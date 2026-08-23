"""
GCP Cloud Storage resource configuration collector.
"""
from app.collectors.base import BaseCollector

class StorageCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of GCP Storage Buckets.
    """
    def collect_resources(self):
        return []
