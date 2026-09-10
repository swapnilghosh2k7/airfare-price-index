"""
Pydantic Schemas for API Request/Response Serialization
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RouteBase(BaseModel):
    origin: str
    destination: str
    route_code: str
    region: Optional[str] = None
    weight: float
    traffic_volume: int
    is_active: bool = True

class RouteSchema(RouteBase):
    route_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RouteWeightUpdate(BaseModel):
    route_code: str
    weight: float

class AirlineSchema(BaseModel):
    airline_id: int
    airline_name: str
    iata_code: str
    tier: str
    market_share: float
    is_active: bool

    class Config:
        from_attributes = True

class SourceSchema(BaseModel):
    source_id: int
    source_name: str
    source_type: str
    domain: Optional[str] = None
    enabled: bool
    robots_allowed: bool
    rate_limit_rps: float
    status: str
    last_scrape_at: Optional[datetime] = None
    captcha_detected_count: int
    requests_successful: int
    requests_failed: int
    records_collected: int
    records_rejected: int

    class Config:
        from_attributes = True

class FareObservationSchema(BaseModel):
    observation_id: str
    timestamp: datetime
    search_date: date
    travel_date: date
    origin: str
    destination: str
    route: str
    airline: str
    source: str
    source_type: str
    flight_number: str
    departure_time: Optional[str] = None
    arrival_time: Optional[str] = None
    duration: Optional[str] = None
    stops: int = 0
    fare_class: str = "Economy"
    base_fare: float
    taxes: float
    airport_fee: float
    user_development_fee: float
    convenience_fee: float
    fuel_surcharge: float
    total_fare: float
    currency: str = "INR"
    advance_purchase_days: int
    z_score: Optional[float] = 0.0
    is_outlier: Optional[bool] = False

    class Config:
        from_attributes = True

class FareFilterParams(BaseModel):
    route: Optional[str] = None
    airline: Optional[str] = None
    source: Optional[str] = None
    advance_purchase_days: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    limit: int = 50
    offset: int = 0

class RejectedObservationSchema(BaseModel):
    rejection_id: str
    timestamp: datetime
    route: Optional[str] = None
    airline: Optional[str] = None
    source: Optional[str] = None
    base_fare: Optional[float] = None
    total_fare: Optional[float] = None
    rejection_reason: str
    rejection_details: Optional[str] = None
    rejected_at: datetime

    class Config:
        from_attributes = True

class IndexCurrentResponse(BaseModel):
    apix_value: float
    index_date: date
    daily_change_pct: float
    weekly_change_pct: float
    monthly_change_pct: float
    average_domestic_fare: float
    base_period_date: str
    base_period_fare: float
    total_observations: int
    active_routes_count: int
    active_airlines_count: int
    calculated_at: datetime
    frequency: str = "DAILY"

class IndexPoint(BaseModel):
    date: str
    apix_value: float
    average_fare: float
    daily_change_pct: Optional[float] = 0.0
    observation_count: int

class IndexHistoryResponse(BaseModel):
    frequency: str
    points: List[IndexPoint]
    base_period_date: str
    total_points: int

class RouteAnalyticsResponse(BaseModel):
    route_code: str
    origin: str
    destination: str
    current_avg_fare: float
    base_avg_fare: float
    price_relative: float
    weight: float
    volatility_pct: float
    observation_count: int
    airline_breakdown: List[Dict[str, Any]]
    lead_time_fares: Dict[str, float]

class LeadTimeElasticityPoint(BaseModel):
    advance_days: int
    window_label: str  # e.g. T+1, T+7
    average_fare: float
    price_multiplier: float
    pct_change_from_next: Optional[float] = 0.0
    observation_count: int

class BacktestSummaryResponse(BaseModel):
    mae: float
    mape: float
    rmse: float
    correlation: float
    bias: float
    sample_size: int
    benchmark_source: str
    date_range: str
    series: List[Dict[str, Any]]

class ScraperStatusResponse(BaseModel):
    sources: List[SourceSchema]
    total_sources: int
    active_sources: int
    live_count: int
    mock_count: int
    error_count: int
    total_collected: int
    total_rejected: int
    last_run_at: Optional[datetime] = None
    next_scheduled_run: Optional[datetime] = None
    scheduler_active: bool = True

class ScraperTriggerResponse(BaseModel):
    run_id: str
    status: str
    records_collected: int
    records_cleaned: int
    records_rejected: int
    message: str

class DataQualityMetrics(BaseModel):
    total_raw_collected: int
    total_clean_accepted: int
    total_rejected: int
    clean_rate_pct: float
    duplicate_rate_pct: float
    outlier_rate_pct: float
    component_mismatch_rate_pct: float
    rejection_reasons_breakdown: Dict[str, int]
    last_cleaned_at: Optional[datetime] = None

class CPIAugmentationResponse(BaseModel):
    title: str = "Experimental Airfare Price Index for CPI Augmentation"
    disclaimer: str
    comparison_dimensions: List[Dict[str, Any]]
    impact_simulation: Dict[str, Any]
