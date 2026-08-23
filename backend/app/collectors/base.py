"""
Base collector class definitions.
"""
from abc import ABC, abstractmethod

class BaseCollector(ABC):
    """
    Abstract Base Class that every cloud service collector must implement.
    """
    @abstractmethod
    def collect_resources(self):
        """
        Collect resources from the cloud provider and return normalized records.
        """
        pass
