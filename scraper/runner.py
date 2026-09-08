"""Unified CLI runner for AirFareX airline scrapers.
Allows running a single airline or all 5 airlines with custom routes,
lead times, and optional demo mode.
"""
import argparse
import asyncio
import logging
import os
import pathlib
import sys
from typing import Dict, List, Type

# Ensure project root is in sys.path
PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scraper.air_india import AirIndiaScraper
from scraper.air_india_express import AirIndiaExpressScraper
from scraper.akasa import AkasaScraper
from scraper.common.base_scraper import BaseScraper
from scraper.indigo import IndigoScraper
from scraper.spicejet import SpiceJetScraper

logger = logging.getLogger("scraper.runner")

AIRLINE_SCRAPERS: Dict[str, Type[BaseScraper]] = {
    "indigo": IndigoScraper,
    "air_india": AirIndiaScraper,
    "air_india_express": AirIndiaExpressScraper,
    "akasa": AkasaScraper,
    "spicejet": SpiceJetScraper,
}


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    parser = argparse.ArgumentParser(description="AirFareX Airline Scrapers Runner")
    parser.add_argument(
        "--airline",
        default="all",
        choices=["all"] + list(AIRLINE_SCRAPERS.keys()),
        help="Airline to scrape (or 'all' for all 5 carriers)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode using synthetic seeder (skips live network requests)",
    )
    parser.add_argument(
        "--routes",
        type=str,
        default="",
        help="Comma-separated route pairs to scrape (e.g. 'DEL-BOM,DEL-BLR'). Defaults to config/routes.yaml",
    )
    parser.add_argument(
        "--lead-times",
        type=str,
        default="",
        help="Comma-separated advance windows in days (e.g. '1,7,15'). Defaults to config/advance_windows.yaml",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Display browser UI instead of headless",
    )

    args = parser.parse_args()

    # Parse custom routes if provided
    selected_routes = None
    if args.routes:
        selected_routes = []
        for pair in args.routes.split(","):
            pair = pair.strip().upper()
            if "-" in pair:
                orig, dest = pair.split("-", 1)
                selected_routes.append({"origin": orig, "destination": dest, "route_code": pair})

    # Parse custom lead times if provided
    selected_windows = None
    if args.lead_times:
        selected_windows = [int(x.strip()) for x in args.lead_times.split(",") if x.strip()]

    target_airlines = list(AIRLINE_SCRAPERS.keys()) if args.airline == "all" else [args.airline]

    total_quotes = 0
    print("=" * 60)
    print(f"Starting AirFareX Scraper Run | Mode: {'DEMO' if args.demo else 'LIVE'}")
    print(f"Target Carriers: {', '.join(target_airlines)}")
    print("=" * 60)

    for airline_key in target_airlines:
        scraper_cls = AIRLINE_SCRAPERS[airline_key]
        scraper = scraper_cls(demo_mode=args.demo, headless=not args.no_headless)
        try:
            quotes = await scraper.run(selected_routes=selected_routes, selected_windows=selected_windows)
            total_quotes += len(quotes)
            print(f"[{scraper.carrier_name}] Finished: {len(quotes)} quotes recorded.")
        except Exception as exc:
            logger.error("Error running scraper for %s: %s", airline_key, exc, exc_info=True)

    print("=" * 60)
    print(f"Scrape Session Complete! Total Quotes Persisted: {total_quotes}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
