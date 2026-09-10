"""
Application Configuration for APIx Platform
"""

import os
from datetime import date, datetime, timedelta
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent
DATA_DIR = PROJECT_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "clean"
REFERENCE_DATA_DIR = DATA_DIR / "reference"

for d in [DATA_DIR, RAW_DATA_DIR, CLEAN_DATA_DIR, REFERENCE_DATA_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'apix.db'}")

# Index Parameters
PROJECT_TITLE = "APIx: Real-time Airfare Price Index for India"
VERSION = "1.0.0"
DEMO_MODE_DEFAULT = True

# Advance Purchase Windows
ADVANCE_PURCHASE_WINDOWS = [1, 7, 15, 30, 45]

# Base Period Reference (Defaults to 30 days prior to current cycle)
BASE_PERIOD_DAYS_AGO = 30
BASE_PERIOD_DATE = (date.today() - timedelta(days=BASE_PERIOD_DAYS_AGO)).isoformat()

# Default Domestic Route Basket (20 Top City-Pairs) with initial DGCA passenger traffic weights
# Weights sum to 1.0 (100%)
INITIAL_ROUTES = [
    {"origin": "DEL", "destination": "BOM", "route_code": "DEL-BOM", "region": "North-West", "weight": 0.125, "traffic_volume": 420000},
    {"origin": "BOM", "destination": "DEL", "route_code": "BOM-DEL", "region": "West-North", "weight": 0.120, "traffic_volume": 410000},
    {"origin": "DEL", "destination": "BLR", "route_code": "DEL-BLR", "region": "North-South", "weight": 0.085, "traffic_volume": 290000},
    {"origin": "BLR", "destination": "DEL", "route_code": "BLR-DEL", "region": "South-North", "weight": 0.080, "traffic_volume": 280000},
    {"origin": "BOM", "destination": "BLR", "route_code": "BOM-BLR", "region": "West-South", "weight": 0.065, "traffic_volume": 220000},
    {"origin": "BLR", "destination": "BOM", "route_code": "BLR-BOM", "region": "South-West", "weight": 0.060, "traffic_volume": 210000},
    {"origin": "DEL", "destination": "HYD", "route_code": "DEL-HYD", "region": "North-South", "weight": 0.055, "traffic_volume": 190000},
    {"origin": "HYD", "destination": "DEL", "route_code": "HYD-DEL", "region": "South-North", "weight": 0.050, "traffic_volume": 180000},
    {"origin": "DEL", "destination": "CCU", "route_code": "DEL-CCU", "region": "North-East", "weight": 0.050, "traffic_volume": 175000},
    {"origin": "CCU", "destination": "DEL", "route_code": "CCU-DEL", "region": "East-North", "weight": 0.045, "traffic_volume": 165000},
    {"origin": "MAA", "destination": "DEL", "route_code": "MAA-DEL", "region": "South-North", "weight": 0.040, "traffic_volume": 140000},
    {"origin": "DEL", "destination": "MAA", "route_code": "DEL-MAA", "region": "North-South", "weight": 0.040, "traffic_volume": 140000},
    {"origin": "BOM", "destination": "HYD", "route_code": "BOM-HYD", "region": "West-South", "weight": 0.035, "traffic_volume": 125000},
    {"origin": "HYD", "destination": "BOM", "route_code": "HYD-BOM", "region": "South-West", "weight": 0.030, "traffic_volume": 115000},
    {"origin": "BOM", "destination": "MAA", "route_code": "BOM-MAA", "region": "West-South", "weight": 0.030, "traffic_volume": 110000},
    {"origin": "MAA", "destination": "BOM", "route_code": "MAA-BOM", "region": "South-West", "weight": 0.025, "traffic_volume": 95000},
    {"origin": "BLR", "destination": "HYD", "route_code": "BLR-HYD", "region": "South-South", "weight": 0.030, "traffic_volume": 110000},
    {"origin": "DEL", "destination": "PNQ", "route_code": "DEL-PNQ", "region": "North-West", "weight": 0.030, "traffic_volume": 105000},
    {"origin": "BOM", "destination": "GOI", "route_code": "BOM-GOI", "region": "West-West", "weight": 0.025, "traffic_volume": 90000},
    {"origin": "DEL", "destination": "GOI", "route_code": "DEL-GOI", "region": "North-West", "weight": 0.020, "traffic_volume": 80000},
]

# Tracked Airlines
INITIAL_AIRLINES = [
    {"airline_name": "IndiGo", "iata_code": "6E", "tier": "LCC", "market_share": 0.605},
    {"airline_name": "Air India", "iata_code": "AI", "tier": "FSC", "market_share": 0.145},
    {"airline_name": "Air India Express", "iata_code": "IX", "tier": "LCC", "market_share": 0.075},
    {"airline_name": "Akasa Air", "iata_code": "QP", "tier": "LCC", "market_share": 0.050},
    {"airline_name": "SpiceJet", "iata_code": "SG", "tier": "LCC", "market_share": 0.040},
]

# Tracked Sources (5 Airlines + 6 OTAs)
INITIAL_SOURCES = [
    # Airlines
    {"source_name": "IndiGo Portal", "source_type": "AIRLINE", "domain": "goindigo.in", "rate_limit_rps": 1.0, "status": "LIVE"},
    {"source_name": "Air India Portal", "source_type": "AIRLINE", "domain": "airindia.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "Air India Express Portal", "source_type": "AIRLINE", "domain": "airindiaexpress.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "Akasa Air Portal", "source_type": "AIRLINE", "domain": "akasaair.com", "rate_limit_rps": 1.0, "status": "MOCK"},
    {"source_name": "SpiceJet Portal", "source_type": "AIRLINE", "domain": "spicejet.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    # OTAs
    {"source_name": "MakeMyTrip", "source_type": "OTA", "domain": "makemytrip.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "Yatra", "source_type": "OTA", "domain": "yatra.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "EaseMyTrip", "source_type": "OTA", "domain": "easemytrip.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "Cleartrip", "source_type": "OTA", "domain": "cleartrip.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "Ixigo", "source_type": "OTA", "domain": "ixigo.com", "rate_limit_rps": 0.5, "status": "MOCK"},
    {"source_name": "Goibibo", "source_type": "OTA", "domain": "goibibo.com", "rate_limit_rps": 0.5, "status": "MOCK"},
]
