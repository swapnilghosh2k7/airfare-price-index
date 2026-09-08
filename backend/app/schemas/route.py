from pydantic import BaseModel, ConfigDict
from typing import Optional

class RouteSchema(BaseModel):
    id: int
    route_code: str
    origin: str
    destination: str
    origin_city: str
    destination_city: str
    weight: float
    active: bool

    model_config = ConfigDict(from_attributes=True)
