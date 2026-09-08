from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime, date

class FareQuoteSchema(BaseModel):
    id: int
    observation_timestamp: datetime
    origin: str
    destination: str
    departure_date: date
    lead_time_days: int
    carrier: str
    flight_number: str
    fare_class: str
    base_fare: float
    taxes: float
    airport_fee: float
    fuel_surcharge: float
    user_development_fee: float
    convenience_fee: float
    other_fee: float
    total_fare: float
    currency: str
    source: str
    source_url: Optional[str] = None
    availability_status: str
    collection_status: str
    raw_hash: str

    model_config = ConfigDict(from_attributes=True)

class PaginatedFareQuotes(BaseModel):
    total: int
    page: int
    size: int
    pages: int
    data: List[FareQuoteSchema]
