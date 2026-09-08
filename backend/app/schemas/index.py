from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import date

class IndexObservationSchema(BaseModel):
    id: int
    observation_date: date
    route_code: str
    lead_time_bucket: int
    route_index: float
    national_index: float
    base_period: str
    weight: float
    sample_count: int
    methodology_version: str

    model_config = ConfigDict(from_attributes=True)

class IndexSummaryResponse(BaseModel):
    latest_date: date
    national_apix: float
    daily_change_pct: float
    weekly_change_pct: float
    monthly_change_pct: float
    total_observations: int
    base_period: str
    methodology_version: str
