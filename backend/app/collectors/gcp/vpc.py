"""
GCP VPC and firewall configuration collector.
"""
from app.collectors.base import BaseCollector

class VPCCollector(BaseCollector):
    """
    Retrieves and normalizes configuration settings of GCP VPC network policies and firewalls.
    """
    def collect_resources(self):
        return []
