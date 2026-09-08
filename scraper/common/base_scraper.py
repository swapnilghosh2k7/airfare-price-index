"""Base asynchronous Playwright scraper for Indian airlines.
Handles common lifecycle: browser initialization, robots.txt checking,
rate limiting, CAPTCHA/block detection, error logging, fare decomposition fallback,
database persistence, and demo mode delegation.
"""
import abc
import asyncio
import datetime
import logging
import os
import pathlib
import sys
from typing import Any, Dict, List, Optional

import yaml
from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from cleaning.fare_decomposition import decompose_fare
from database.models import FareQuote, save_fare_quote
from scraper.common.rate_limiter import limit_rate
from scraper.common.robots_check import is_allowed

logger = logging.getLogger("scraper.base")

# Known CAPTCHA and anti-bot signatures across Indian travel portals
CAPTCHA_INDICATORS = [
    "verify you are human",
    "cf-turnstile",
    "g-recaptcha",
    "hcaptcha",
    "perimeterx",
    "px-captcha",
    "kasada",
    "access denied",
    "pardon our interruption",
    "attention required! | cloudflare",
    "bot detection",
    "security check",
    "blocked by akamai",
]


class BaseScraper(abc.ABC):
    """Abstract base class for airline web scrapers."""

    carrier_name: str = "Unknown Carrier"
    carrier_code: str = "XX"
    base_url: str = ""
    source_id: str = "generic_airline"
    source_type: str = "airline_direct"
    default_timeout_ms: int = 30000

    def __init__(
        self,
        routes_path: Optional[str] = None,
        advance_windows_path: Optional[str] = None,
        demo_mode: bool = False,
        headless: bool = True,
    ):
        self.routes_path = routes_path or self._resolve_config_path("routes.yaml")
        self.advance_windows_path = advance_windows_path or self._resolve_config_path("advance_windows.yaml")
        self.demo_mode = demo_mode or os.getenv("DEMO_MODE", "").lower() in ("1", "true", "yes")
        self.headless = headless
        self.routes = self.load_routes()
        self.advance_windows = self.load_advance_windows()

    @staticmethod
    def _resolve_config_path(filename: str) -> str:
        # Check current directory / scraper/config
        candidates = [
            pathlib.Path("scraper/config") / filename,
            pathlib.Path(__file__).parent.parent / "config" / filename,
            pathlib.Path("config") / filename,
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate.resolve())
        return str((pathlib.Path("scraper/config") / filename).resolve())

    def load_routes(self) -> List[Dict[str, Any]]:
        """Load target routes from YAML config."""
        try:
            if os.path.exists(self.routes_path):
                with open(self.routes_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    routes = data.get("routes", [])
                    return [r for r in routes if r.get("active", True)]
        except Exception as exc:
            logger.warning("Could not load routes from %s (%s). Using defaults.", self.routes_path, exc)

        return [
            {"origin": "DEL", "destination": "BOM", "route_code": "DEL-BOM"},
            {"origin": "DEL", "destination": "BLR", "route_code": "DEL-BLR"},
            {"origin": "BOM", "destination": "BLR", "route_code": "BOM-BLR"},
        ]

    def load_advance_windows(self) -> List[int]:
        """Load advance lead-time windows in days from YAML config."""
        try:
            if os.path.exists(self.advance_windows_path):
                with open(self.advance_windows_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    windows = data.get("windows", [])
                    return [w["days"] if isinstance(w, dict) else int(w) for w in windows]
        except Exception as exc:
            logger.warning("Could not load advance windows from %s (%s). Using defaults.", self.advance_windows_path, exc)

        return [1, 7, 15, 30, 45]

    async def detect_captcha_or_block(self, page: Page) -> Optional[str]:
        """Inspect page title, URL, and HTML body for CAPTCHAs or blocking screens."""
        try:
            title = (await page.title()).lower()
            content = (await page.content()).lower()

            for indicator in CAPTCHA_INDICATORS:
                if indicator in title or indicator in content:
                    return indicator
        except Exception:
            pass
        return None

    def apply_fare_decomposition_if_needed(self, quote: Dict[str, Any]) -> Dict[str, Any]:
        """If breakdown (taxes, fees, fuel) is zero but total_fare is given,

        apply fare_decomposition heuristics.
        """
        total = float(quote.get("total_fare", 0.0) or 0.0)
        base = float(quote.get("base_fare", 0.0) or 0.0)
        taxes = float(quote.get("taxes", 0.0) or 0.0)
        fuel = float(quote.get("fuel_surcharge", 0.0) or 0.0)

        if total > 0 and (base <= 0 or (taxes <= 0 and fuel <= 0)):
            breakdown = decompose_fare(
                total_fare=total,
                origin=quote.get("origin", ""),
                destination=quote.get("destination", ""),
                fare_class=quote.get("fare_class", "Economy"),
            )
            quote["base_fare"] = breakdown["base_fare"]
            quote["taxes"] = breakdown["taxes"]
            quote["airport_fee"] = breakdown["airport_fee"]
            quote["fuel_surcharge"] = breakdown["fuel_surcharge"]
            quote["user_development_fee"] = breakdown["user_development_fee"]
            quote["convenience_fee"] = breakdown["convenience_fee"]
            quote["other_fee"] = breakdown["other_fee"]
            quote["total_fare"] = breakdown["total_fare"]

        return quote

    def save_quote_to_db(self, quote: Dict[str, Any]) -> Optional[FareQuote]:
        """Save quote to the database tagged with carrier source and source_type."""
        try:
            quote_copy = dict(quote)
            quote_copy["carrier"] = quote_copy.get("carrier") or self.carrier_name
            quote_copy["source"] = self.source_id
            quote_copy["source_type"] = self.source_type
            quote_copy["currency"] = quote_copy.get("currency", "INR")
            quote_copy = self.apply_fare_decomposition_if_needed(quote_copy)
            saved = save_fare_quote(quote_copy)
            return saved
        except Exception as exc:
            logger.error("Failed to save quote for %s flight %s: %s", self.carrier_name, quote.get("flight_number"), exc)
            return None

    @abc.abstractmethod
    async def extract_fares(
        self,
        page: Page,
        origin: str,
        destination: str,
        departure_date: datetime.date,
        lead_time_days: int,
    ) -> List[Dict[str, Any]]:
        """Airline-specific navigation and fare extraction logic.

        Must extract: carrier, flight_number, fare_class, base_fare,
        taxes/fees breakdown (or total), seats_remaining (if shown),
        availability_status ('AVAILABLE' or 'SOLD_OUT').
        """
        raise NotImplementedError

    async def run_query(
        self,
        page: Page,
        origin: str,
        destination: str,
        departure_date: datetime.date,
        lead_time_days: int,
    ) -> List[Dict[str, Any]]:
        """Safely execute a single search query without crashing on failures."""
        route_str = f"{origin}->{destination} (T+{lead_time_days}, date: {departure_date})"
        logger.info("[%s] Initiating search for %s", self.carrier_name, route_str)

        # 1. Robots.txt check
        if not is_allowed(self.base_url):
            logger.warning("[%s] Scraping disallowed by robots.txt for %s. Skipping query.", self.carrier_name, self.base_url)
            return []

        # 2. Rate limiter delay
        await limit_rate(self.base_url)

        try:
            # 3. Airline-specific extraction
            raw_quotes = await self.extract_fares(
                page=page,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                lead_time_days=lead_time_days,
            )

            # 4. Check for CAPTCHA / Access Block screens
            block_reason = await self.detect_captcha_or_block(page)
            if block_reason:
                logger.warning(
                    "[%s] CAPTCHA / Bot detection triggered (%s) on %s. Never attempting bypass. Moving to next query.",
                    self.carrier_name,
                    block_reason,
                    route_str,
                )
                return []

            # 5. Persist successful quotes to DB
            saved_quotes = []
            for q in raw_quotes:
                saved = self.save_quote_to_db(q)
                if saved:
                    saved_quotes.append(q)

            logger.info("[%s] Successfully extracted and stored %d quotes for %s", self.carrier_name, len(saved_quotes), route_str)
            return raw_quotes

        except asyncio.TimeoutError as te:
            logger.warning("[%s] Timeout while waiting for results for %s (%s). Moving to next query.", self.carrier_name, route_str, te)
            return []
        except Exception as exc:
            logger.error("[%s] Failure processing query for %s: %s. Moving to next query.", self.carrier_name, route_str, exc, exc_info=True)
            return []

    async def run(
        self,
        selected_routes: Optional[List[Dict[str, Any]]] = None,
        selected_windows: Optional[List[int]] = None,
    ) -> List[Dict[str, Any]]:
        """Run full scraper across configured routes and advance purchase windows."""
        routes = selected_routes or self.routes
        windows = selected_windows or self.advance_windows
        today = datetime.date.today()

        # Handle Demo Mode: skip live browser, invoke seed_mock_data
        if self.demo_mode:
            logger.info("[%s] DEMO_MODE active: using seed_mock_data generator.", self.carrier_name)
            try:
                import seed_mock_data

                all_demo_quotes = []
                for r in routes:
                    orig = r["origin"]
                    dest = r["destination"]
                    for lead in windows:
                        dep_date = today + datetime.timedelta(days=lead)
                        demo_quotes = seed_mock_data.generate_airline_mock_quotes(
                            airline=self.source_id,
                            origin=orig,
                            destination=dest,
                            departure_date=dep_date,
                            lead_time_days=lead,
                        )
                        for q in demo_quotes:
                            self.save_quote_to_db(q)
                            all_demo_quotes.append(q)
                logger.info("[%s] Demo execution generated and stored %d quotes.", self.carrier_name, len(all_demo_quotes))
                return all_demo_quotes
            except Exception as exc:
                logger.error("[%s] Error running demo mode with seed_mock_data: %s", self.carrier_name, exc)
                return []

        # Live Playwright scraping
        collected_quotes: List[Dict[str, Any]] = []
        async with async_playwright() as p:
            logger.info("[%s] Launching Chromium browser (headless=%s)", self.carrier_name, self.headless)
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-blink-features=AutomationControlled"],
            )
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                viewport={"width": 1366, "height": 768},
            )
            page = await context.new_page()
            page.set_default_timeout(self.default_timeout_ms)

            try:
                for r in routes:
                    orig = r["origin"]
                    dest = r["destination"]
                    for lead in windows:
                        dep_date = today + datetime.timedelta(days=lead)
                        quotes = await self.run_query(
                            page=page,
                            origin=orig,
                            destination=dest,
                            departure_date=dep_date,
                            lead_time_days=lead,
                        )
                        collected_quotes.extend(quotes)
            finally:
                await context.close()
                await browser.close()

        logger.info("[%s] Scraper finished. Total quotes collected: %d", self.carrier_name, len(collected_quotes))
        return collected_quotes
