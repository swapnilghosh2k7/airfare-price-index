import os
import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"

class DatabaseSettings(BaseModel):
    db_type: str = "sqlite"
    sqlite_url: str = f"sqlite:///{PROJECT_ROOT}/airfarex.db"
    postgres_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/airfarex"

class BasePeriodSettings(BaseModel):
    days: int = 30
    mode: str = "relative_start"
    base_period_code: str = "2026-08-BASE30"

class IndexingSettings(BaseModel):
    methodology_version: str = "APIX_v1"
    representative_price_metric: str = "median"
    trimmed_mean_cutoff: float = 0.10
    base_period: BasePeriodSettings = BasePeriodSettings()
    lead_time_buckets: List[int] = [1, 7, 15, 30, 45]

class QualitySettings(BaseModel):
    outlier_method: str = "MAD"
    mad_threshold: float = 3.0
    iqr_multiplier: float = 1.5
    duplicate_check_fields: List[str] = [
        "origin", "destination", "departure_date",
        "carrier", "flight_number", "fare_class",
        "source", "observation_timestamp"
    ]

class AppSettings(BaseModel):
    name: str = "AirFareX - Indian Airfare Price Index"
    version: str = "1.0.0"
    demo_mode: bool = True
    environment: str = "development"
    database_url: str = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/airfarex.db")
    database: DatabaseSettings = DatabaseSettings()
    indexing: IndexingSettings = IndexingSettings()
    quality: QualitySettings = QualitySettings()

def load_settings() -> AppSettings:
    settings_file = CONFIG_DIR / "settings.yaml"
    if settings_file.exists():
        with open(settings_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            app_data = data.get("app", {})
            db_data = data.get("database", {})
            idx_data = data.get("indexing", {})
            qual_data = data.get("quality", {})
            
            return AppSettings(
                name=app_data.get("name", "AirFareX"),
                version=app_data.get("version", "1.0.0"),
                demo_mode=app_data.get("demo_mode", True),
                environment=app_data.get("environment", "development"),
                database_url=os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/airfarex.db"),
                database=DatabaseSettings(**db_data),
                indexing=IndexingSettings(
                    methodology_version=idx_data.get("methodology_version", "APIX_v1"),
                    representative_price_metric=idx_data.get("representative_price_metric", "median"),
                    trimmed_mean_cutoff=idx_data.get("trimmed_mean_cutoff", 0.10),
                    base_period=BasePeriodSettings(**idx_data.get("base_period", {})),
                    lead_time_buckets=idx_data.get("lead_time_buckets", [1, 7, 15, 30, 45])
                ),
                quality=QualitySettings(**qual_data)
            )
    return AppSettings()

settings = load_settings()
