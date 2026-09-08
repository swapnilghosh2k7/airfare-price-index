from pydantic import BaseModel, ConfigDict

class CarrierSchema(BaseModel):
    id: int
    name: str
    iata_code: str
    source_type: str
    active: bool

    model_config = ConfigDict(from_attributes=True)
