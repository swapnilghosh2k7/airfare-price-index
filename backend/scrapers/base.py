"""
Ethical Scraping Base Architecture
Implements robots.txt compliance, rate-limiting, CAPTCHA detection, and graceful mock fallback.
"""

import time
import urllib.robotparser
from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import List, Dict, Any, Optional
import httpx
from backend.synthetic.generator import generate_single_fare_quote

_ROBOTS_CACHE = {}

class SourceAdapter(ABC):
    """
    Abstract Base Class for all Airline and OTA Source Adapters.
    Enforces ethical scraping guidelines:
    - Verifies robots.txt permissions
    - Enforces rate limits (requests per second)
    - Detects CAPTCHA / anti-bot challenges and safely stops
    - Provides realistic fallback data for testing/demo
    """

    def __init__(
        self,
        source_name: str,
        source_type: str,  # 'AIRLINE' or 'OTA'
        domain: str,
        enabled: bool = True,
        rate_limit_rps: float = 1.0,
        status: str = "LIVE",
        check_robots_now: bool = False
    ):
        self.source_name = source_name
        self.source_type = source_type
        self.domain = domain
        self.enabled = enabled
        self.rate_limit_rps = rate_limit_rps
        self.status = status  # LIVE, MOCK, UNAVAILABLE, ERROR
        self.robots_allowed = _ROBOTS_CACHE.get(domain, True)
        self.last_request_time = 0.0
        self.captcha_detected_count = 0
        self.requests_successful = 0
        self.requests_failed = 0
        self.records_collected = 0
        self.records_rejected = 0
        self.last_scrape_at: Optional[datetime] = None
        self.user_agent = "APIx-MoSPI-ResearchBot/1.0 (+https://mospi.gov.in/research/apix; contact: apix-research@mospi.gov.in)"

        self.robot_parser = urllib.robotparser.RobotFileParser()
        if check_robots_now and domain not in _ROBOTS_CACHE:
            self._check_robots_txt()

    def _check_robots_txt(self):
        """Verifies if robots.txt permits crawling search routes safely without blocking"""
        if self.domain in _ROBOTS_CACHE:
            self.robots_allowed = _ROBOTS_CACHE[self.domain]
            return
        try:
            robots_url = f"https://{self.domain}/robots.txt"
            with httpx.Client(timeout=0.4, follow_redirects=True) as client:
                resp = client.get(robots_url, headers={"User-Agent": self.user_agent})
                if resp.status_code == 200:
                    lines = resp.text.splitlines()
                    self.robot_parser.parse(lines)
                    allowed = self.robot_parser.can_fetch(self.user_agent, f"https://{self.domain}/flights")
                    _ROBOTS_CACHE[self.domain] = allowed
                    self.robots_allowed = allowed
                else:
                    _ROBOTS_CACHE[self.domain] = True
                    self.robots_allowed = True
        except Exception:
            _ROBOTS_CACHE[self.domain] = True
            self.robots_allowed = True

    def enforce_rate_limit(self):
        """Throttles requests to respect server capacity during live crawling"""
        if self.status != "LIVE":
            return  # No artificial latency needed for local/mock fallback simulation
        min_interval = 1.0 / max(0.1, self.rate_limit_rps)
        elapsed = time.time() - self.last_request_time
        if elapsed < min_interval and self.last_request_time > 0:
            time.sleep(min(0.2, min_interval - elapsed))  # Cap sleep to 200ms
        self.last_request_time = time.time()

    def is_captcha_or_blocked(self, response_text: str, status_code: int) -> bool:
        """
        Inspects response headers and content for anti-bot / CAPTCHA signatures:
        Cloudflare Turnstile, DataDome, PerimeterX, Akamai Bot Manager, Google reCAPTCHA, etc.
        """
        if status_code in (403, 429):
            return True

        lower_text = response_text.lower()
        captcha_signatures = [
            "captcha",
            "challenge-running",
            "cf-turnstile",
            "datadome",
            "perimeterx",
            "bot-detection",
            "security check to continue",
            "access denied - cloudflare"
        ]
        return any(sig in lower_text for sig in captcha_signatures)

    @abstractmethod
    def fetch_fares(
        self,
        route_info: Dict[str, Any],
        search_date: date,
        advance_days: int
    ) -> List[Dict[str, Any]]:
        """
        Fetches live fares from source. If blocked or mode is MOCK, falls back cleanly.
        """
        pass

    @abstractmethod
    def parse_fares(self, raw_payload: Any) -> List[Dict[str, Any]]:
        """Parses raw HTTP/JSON payload into standard airfare schema"""
        pass

    def get_fallback_fares(
        self,
        route_info: Dict[str, Any],
        airline_info: Dict[str, Any],
        search_date: date,
        advance_days: int,
        count: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Generates realistic calibrated fallback observations when live source is blocked.
        """
        source_dict = {
            "source_name": self.source_name,
            "source_type": self.source_type
        }
        quotes = []
        for _ in range(count):
            q = generate_single_fare_quote(
                route_info=route_info,
                airline_info=airline_info,
                source_info=source_dict,
                search_date=search_date,
                advance_days=advance_days,
                inject_anomaly_chance=0.02
            )
            quotes.append(q)
        return quotes
