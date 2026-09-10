"""
Online Travel Aggregator (OTA) Source Adapters
Implements adapters for MakeMyTrip, Yatra, EaseMyTrip, Cleartrip, Ixigo, and Goibibo.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional
import random
from backend.scrapers.base import SourceAdapter
from backend.config import INITIAL_AIRLINES

class BaseOTAAdapter(SourceAdapter):
    """Base class for Indian OTA aggregators"""
    def __init__(self, name: str, domain: str, rps: float = 0.5, status: str = "MOCK"):
        super().__init__(
            source_name=name,
            source_type="OTA",
            domain=domain,
            enabled=True,
            rate_limit_rps=rps,
            status=status
        )

    def fetch_fares(
        self,
        route_info: Dict[str, Any],
        search_date: date,
        advance_days: int
    ) -> List[Dict[str, Any]]:
        self.enforce_rate_limit()
        # OTAs aggregate multiple airlines
        selected_airline = random.choice(INITIAL_AIRLINES)
        quotes = self.get_fallback_fares(route_info, selected_airline, search_date, advance_days, count=2)
        self.records_collected += len(quotes)
        self.requests_successful += 1
        self.last_scrape_at = datetime.utcnow()
        return quotes

    def parse_fares(self, raw_payload: Any) -> List[Dict[str, Any]]:
        return []

class MakeMyTripAdapter(BaseOTAAdapter):
    def __init__(self):
        super().__init__("MakeMyTrip", "makemytrip.com", rps=0.5, status="MOCK")

class YatraAdapter(BaseOTAAdapter):
    def __init__(self):
        super().__init__("Yatra", "yatra.com", rps=0.5, status="MOCK")

class EaseMyTripAdapter(BaseOTAAdapter):
    def __init__(self):
        super().__init__("EaseMyTrip", "easemytrip.com", rps=0.5, status="MOCK")

class CleartripAdapter(BaseOTAAdapter):
    def __init__(self):
        super().__init__("Cleartrip", "cleartrip.com", rps=0.5, status="MOCK")

class IxigoAdapter(BaseOTAAdapter):
    def __init__(self):
        super().__init__("Ixigo", "ixigo.com", rps=0.5, status="MOCK")

class GoibiboAdapter(BaseOTAAdapter):
    def __init__(self):
        super().__init__("Goibibo", "goibibo.com", rps=0.5, status="MOCK")
