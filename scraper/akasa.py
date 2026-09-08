"""Akasa Air (akasaair.com) Asynchronous Playwright Scraper.
Carrier: Akasa Air (IATA: QP)
"""
import argparse
import asyncio
import datetime
import logging
import os
import pathlib
import re
import sys
from typing import Any, Dict, List, Optional

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from playwright.async_api import Page
from scraper.common.base_scraper import BaseScraper

logger = logging.getLogger("scraper.akasa")


def parse_price_str(text: str) -> float:
    """Parse numeric price from string."""
    if not text:
        return 0.0
    clean = re.sub(r"[^\d.]", "", text)
    try:
        return float(clean)
    except ValueError:
        return 0.0


def extract_akasa_quotes_from_dom_or_html(
    html_text: str,
    origin: str,
    destination: str,
    departure_date: datetime.date,
    lead_time_days: int,
) -> List[Dict[str, Any]]:
    """Pure extraction logic from HTML content or DOM snippets.

    Separated for unit testing and offline CI execution without network/browser.
    """
    quotes: List[Dict[str, Any]] = []

    flight_blocks = re.findall(
        r'(<div[^>]*class="[^"]*(?:akasa-flight-card|flightCard|qp-flight-row|flight-card)[^"]*"[^>]*>.*?</div>\s*</div>)',
        html_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not flight_blocks:
        flight_blocks = re.findall(
            r'(<div[^>]*data-testid="flight-card"[^>]*>.*?</div>\s*</div>)',
            html_text,
            re.DOTALL | re.IGNORECASE,
        )

    for block in flight_blocks:
        # Flight Number: QP-xxx
        fn_match = re.search(r'(?:QP[- ]?(\d{3,4}))|(?:flightCode[^>]*>\s*([A-Z0-9 -]+))', block, re.IGNORECASE)
        flight_num = "QP-000"
        if fn_match:
            flt = fn_match.group(1) or fn_match.group(2)
            flt_clean = flt.strip().replace(" ", "-")
            flight_num = flt_clean if flt_clean.startswith("QP") else f"QP-{flt_clean}"

        # Sold Out check
        is_sold_out = bool(re.search(r'(?:sold\s*out|soldOut|unavailable|disabled-fare)', block, re.IGNORECASE))
        status = "SOLD_OUT" if is_sold_out else "AVAILABLE"

        # Seats remaining
        seats_match = re.search(r'(\d+)\s*(?:seats?\s*)?(?:left|remaining|available)', block, re.IGNORECASE)
        seats_remaining = int(seats_match.group(1)) if seats_match else None

        # Fare classes: Saver, Flexi
        fare_classes = ["Flexi", "Saver", "Economy"]
        matched_class = "Saver"
        for fc in fare_classes:
            if fc.lower() in block.lower():
                matched_class = fc
                break

        # Extract total fare, base fare, taxes
        base_match = re.search(r'(?:base[\s_-]*fare)[^>]*>.*?(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)
        base_fare = parse_price_str(base_match.group(1)) if base_match else 0.0

        tax_match = re.search(r'(?:taxes|surcharges|tax|gst)[^>]*>.*?(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)
        taxes = parse_price_str(tax_match.group(1)) if tax_match else 0.0

        total_match = re.search(r'(?:total[\s_-]*fare|final[\s_-]*fare|fare-amount|priceVal)[^>]*>.*?(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)
        if total_match:
            total_fare = parse_price_str(total_match.group(1))
        else:
            all_prices = [parse_price_str(p) for p in re.findall(r'(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)]
            total_fare = max(all_prices) if all_prices else 0.0

        if is_sold_out:
            total_fare = 0.0
            base_fare = 0.0
            taxes = 0.0

        quotes.append({
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
            "lead_time_days": lead_time_days,
            "carrier": "Akasa Air",
            "flight_number": flight_num,
            "fare_class": matched_class,
            "base_fare": base_fare,
            "taxes": taxes,
            "total_fare": total_fare,
            "availability_status": status,
            "seats_remaining": seats_remaining,
            "source": "akasa",
            "source_type": "airline_direct",
            "currency": "INR",
        })

    return quotes


class AkasaScraper(BaseScraper):
    carrier_name = "Akasa Air"
    carrier_code = "QP"
    base_url = "https://www.akasaair.com"
    source_id = "akasa"

    async def extract_fares(
        self,
        page: Page,
        origin: str,
        destination: str,
        departure_date: datetime.date,
        lead_time_days: int,
    ) -> List[Dict[str, Any]]:
        date_str = departure_date.strftime("%Y-%m-%d")
        search_url = (
            f"{self.base_url}/booking"
            f"?origin={origin}&destination={destination}&departureDate={date_str}&adults=1"
        )
        logger.info("[Akasa Air] Navigating to %s", search_url)

        try:
            await page.goto(search_url, wait_until="networkidle", timeout=self.default_timeout_ms)
        except Exception as exc:
            logger.warning("[Akasa Air] Initial goto networkidle timed out (%s), continuing...", exc)

        selectors = [
            ".akasa-flight-card",
            ".flightCard",
            "[data-testid='flight-card']",
            ".qp-flight-row",
        ]
        for sel in selectors:
            try:
                await page.wait_for_selector(sel, timeout=7000)
                break
            except Exception:
                continue

        html_content = await page.content()
        quotes = extract_akasa_quotes_from_dom_or_html(
            html_text=html_content,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            lead_time_days=lead_time_days,
        )

        return quotes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Akasa Air Scraper")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode using mock seeder")
    parser.add_argument("--origin", default="DEL", help="Origin airport code")
    parser.add_argument("--destination", default="BOM", help="Destination airport code")
    parser.add_argument("--advance", type=int, default=7, help="Advance purchase days")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    args = parser.parse_args()

    scraper = AkasaScraper(demo_mode=args.demo, headless=args.headless)
    custom_routes = [{"origin": args.origin, "destination": args.destination, "route_code": f"{args.origin}-{args.destination}"}]
    results = asyncio.run(scraper.run(selected_routes=custom_routes, selected_windows=[args.advance]))
    print(f"Akasa Air Scrape Complete: {len(results)} quotes collected.")
