"""IndiGo (goindigo.in) Asynchronous Playwright Scraper.
Carrier: IndiGo (IATA: 6E)
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

logger = logging.getLogger("scraper.indigo")


def parse_price_str(text: str) -> float:
    """Parse numeric price from string like 'INR 5,499' or '₹5,499.00'."""
    if not text:
        return 0.0
    clean = re.sub(r"[^\d.]", "", text)
    try:
        return float(clean)
    except ValueError:
        return 0.0


def extract_indigo_quotes_from_dom_or_html(
    html_text: str,
    origin: str,
    destination: str,
    departure_date: datetime.date,
    lead_time_days: int,
) -> List[Dict[str, Any]]:
    """Pure extraction logic from HTML content or DOM snippets.

    Separated for unit testing and offline CI execution without network/browser.
    """
    import re
    quotes: List[Dict[str, Any]] = []

    # Match flight card patterns in IndiGo HTML
    # We look for flight item cards or testid containers
    flight_blocks = re.findall(
        r'(<div[^>]*class="[^"]*(?:flight-card|flight-item|booking-row|fare-card)[^"]*"[^>]*>.*?</div>\s*</div>)',
        html_text,
        re.DOTALL | re.IGNORECASE,
    )
    if not flight_blocks:
        # Broader chunking if specific classes changed
        flight_blocks = re.findall(
            r'(<div[^>]*data-testid="flight-card"[^>]*>.*?</div>\s*</div>)',
            html_text,
            re.DOTALL | re.IGNORECASE,
        )

    for block in flight_blocks:
        # Flight Number
        fn_match = re.search(r'(?:6E[- ]?(\d{3,4}))|(?:flight-number[^>]*>\s*([A-Z0-9 -]+))', block, re.IGNORECASE)
        flight_num = "6E-000"
        if fn_match:
            flt = fn_match.group(1) or fn_match.group(2)
            flt_clean = flt.strip().replace(" ", "-")
            flight_num = flt_clean if flt_clean.startswith("6E") else f"6E-{flt_clean}"

        # Sold Out check
        is_sold_out = bool(re.search(r'(?:sold\s*out|fare-sold-out|unavailable)', block, re.IGNORECASE))
        status = "SOLD_OUT" if is_sold_out else "AVAILABLE"

        # Seats remaining (e.g. '4 seats left', '2 seats remaining')
        seats_match = re.search(r'(\d+)\s*(?:seats?\s*)?(?:left|remaining)', block, re.IGNORECASE)
        seats_remaining = int(seats_match.group(1)) if seats_match else None

        # Fare classes & prices (Saver, Flexi Plus, Super 6E)
        fare_classes = ["Saver", "Flexi Plus", "Super 6E"]
        matched_class = "Saver"
        for fc in fare_classes:
            if fc.lower() in block.lower():
                matched_class = fc
                break

        # Extract total fare, base fare, taxes
        base_match = re.search(r'(?:base[\s_-]*fare)[^>]*>.*?(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)
        base_fare = parse_price_str(base_match.group(1)) if base_match else 0.0

        tax_match = re.search(r'(?:taxes|tax|gst|surcharge)[^>]*>.*?(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)
        taxes = parse_price_str(tax_match.group(1)) if tax_match else 0.0

        total_match = re.search(r'(?:total[\s_-]*fare|final[\s_-]*fare|total-price)[^>]*>.*?(?:₹|INR|Rs\.?)\s*([\d,]+(?:\.\d{2})?)', block, re.IGNORECASE)
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
            "carrier": "IndiGo",
            "flight_number": flight_num,
            "fare_class": matched_class,
            "base_fare": base_fare,
            "taxes": taxes,
            "total_fare": total_fare,
            "availability_status": status,
            "seats_remaining": seats_remaining,
            "source": "indigo",
            "source_type": "airline_direct",
            "currency": "INR",
        })

    return quotes


class IndigoScraper(BaseScraper):
    carrier_name = "IndiGo"
    carrier_code = "6E"
    base_url = "https://www.goindigo.in"
    source_id = "indigo"

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
            f"{self.base_url}/booking/flight-select.html"
            f"?indiGoOrigin={origin}&indiGoDestination={destination}"
            f"&departureDate={date_str}&tripType=OW&isPassengerCount=1&isAdultPassenger=1"
        )
        logger.info("[IndiGo] Navigating to %s", search_url)

        try:
            await page.goto(search_url, wait_until="networkidle", timeout=self.default_timeout_ms)
        except Exception as exc:
            logger.warning("[IndiGo] Initial goto networkidle timed out (%s), continuing...", exc)

        # Wait for flight rows or results container
        selectors = [
            ".flight-card",
            ".flight-item",
            "[data-testid='flight-card']",
            ".booking-row",
            ".fare-card",
        ]
        results_found = False
        for sel in selectors:
            try:
                await page.wait_for_selector(sel, timeout=7000)
                results_found = True
                break
            except Exception:
                continue

        if not results_found:
            logger.warning("[IndiGo] Search results selector not found for %s->%s (%s)", origin, destination, date_str)

        html_content = await page.content()
        quotes = extract_indigo_quotes_from_dom_or_html(
            html_text=html_content,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            lead_time_days=lead_time_days,
        )

        return quotes


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="IndiGo Airline Scraper")
    parser.add_argument("--demo", action="store_true", help="Run in demo mode using mock seeder")
    parser.add_argument("--origin", default="DEL", help="Origin airport code")
    parser.add_argument("--destination", default="BOM", help="Destination airport code")
    parser.add_argument("--advance", type=int, default=7, help="Advance purchase days")
    parser.add_argument("--headless", action="store_true", default=True, help="Run headless")
    args = parser.parse_args()

    scraper = IndigoScraper(demo_mode=args.demo, headless=args.headless)
    custom_routes = [{"origin": args.origin, "destination": args.destination, "route_code": f"{args.origin}-{args.destination}"}]
    results = asyncio.run(scraper.run(selected_routes=custom_routes, selected_windows=[args.advance]))
    print(f"IndiGo Scrape Complete: {len(results)} quotes collected.")
