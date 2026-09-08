import time
import urllib.robotparser
from typing import List, Dict, Any, Optional
from datetime import date
import httpx
from collectors.base_provider import FareProvider

class PermittedLiveScraperAdapter(FareProvider):
    USER_AGENT = "AirFareX-Research-Bot/1.0 (+http://airfarex.local/policy)"
    
    def __init__(self, domain: str, min_delay_seconds: float = 5.0):
        self.domain = domain.rstrip("/")
        self.min_delay = min_delay_seconds
        self.last_request_time = 0.0
        self.robot_parser = urllib.robotparser.RobotFileParser()
        self._init_robots_txt()

    def _init_robots_txt(self):
        try:
            robots_url = f"{self.domain}/robots.txt"
            self.robot_parser.set_url(robots_url)
            self.robot_parser.read()
        except Exception:
            pass

    def is_allowed_by_robots_txt(self, url: str) -> bool:
        """Verifies URL permission against robots.txt directives"""
        try:
            return self.robot_parser.can_fetch(self.USER_AGENT, url)
        except Exception:
            return True

    def enforce_rate_limit(self):
        """Enforces conservative rate limiting between consecutive HTTP requests"""
        now = time.time()
        elapsed = now - self.last_request_time
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        self.last_request_time = time.time()

    @property
    def provider_id(self) -> str:
        return "permitted_live_adapter"

    @property
    def provider_name(self) -> str:
        return f"Permitted Live Scraper ({self.domain})"

    async def search_fares(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        lead_time_days: int = 1
    ) -> List[Dict[str, Any]]:
        target_url = f"{self.domain}/search?origin={origin}&dest={destination}&date={departure_date.isoformat()}"
        
        if not self.is_allowed_by_robots_txt(target_url):
            print(f"[AirFareX Ethical Scraper Warning] URL disallowed by robots.txt: {target_url}")
            return []

        self.enforce_rate_limit()

        headers = {"User-Agent": self.USER_AGENT}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(target_url, headers=headers)
                if res.status_code == 200:
                    # Permitted public response parsing logic would go here
                    return []
                else:
                    return []
        except Exception as e:
            print(f"[AirFareX Scraper Notice] Permitted endpoint returned exception: {e}")
            return []
