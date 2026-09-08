from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any

class DataQualitySummarySchema(BaseModel):
    total_quotes: int
    valid_quotes: int
    outlier_quotes: int
    duplicate_quotes: int
    average_quality_score: float
    missing_fields_count: int

class CollectionRunSchema(BaseModel):
    id: int
    started_at: str
    completed_at: str | None = None
    source: str
    routes_requested: int
    quotes_collected: int
    quotes_valid: int
    quotes_rejected: int
    status: str
    error_summary: str | None = None

    model_config = ConfigDict(from_attributes=True)
