from pydantic import BaseModel, ConfigDict


class CloudResource(BaseModel):
    provider: str
    resource_type: str
    resource_id: str
    name: str
    region: str | None = None
    configuration: dict[str, object]


class ResourceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    resource_type: str
    resource_id: str
    name: str
    region: str | None
    configuration_json: str
