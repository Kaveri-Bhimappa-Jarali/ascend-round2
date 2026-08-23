"""
Domain model representing normalized cloud resources.
"""
from pydantic import BaseModel
from typing import Dict, Any

class ResourceModel(BaseModel):
    provider: str
    resource_type: str
    resource_id: str
    resource_name: str
    configuration: Dict[str, Any]
