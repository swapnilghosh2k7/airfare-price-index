"""Comprehensive offline pytest test suite for AirFareX airline scrapers.
Uses saved HTML fixtures and mocks network layers completely so tests run
offline and in CI without opening real browsers or hitting live websites.
"""
import asyncio
import datetime
import os
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).parent.parent.resolve()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from cleaning.fare_decomposition import decompose_fare
from database.models import FareQuote, get_session, init_db, save_fare_quote
from scraper.air_india import AirIndiaScraper, extract_air_india_quotes_from_dom_or_html
from scraper.air_india_express import AirIndiaExpressScraper, extract_air_india_express_quotes_from_dom_or_html
from scraper.akasa import AkasaScraper, extract_akasa_quotes_from_dom_or_html
from scraper.common.base_scraper import BaseScraper
from scraper.common.rate_limiter import RateLimiter
from scraper.common.robots_check import RobotsChecker, is_allowed
from scraper.indigo import IndigoScraper, extract_indigo_quotes_from_dom_or_html
from scraper.spicejet import SpiceJetScraper, extract_spicejet_quotes_from_dom_or_html
import seed_mock_data

FIXTURES_DIR = pathlib.Path(__file__).parent / "fixtures"


def read_fixture(filename: str) -> str:
    path = FIXTURES_DIR / filename
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


# ---------------------------------------------------------------------------
# 1. HTML Extraction Tests for All 5 Airlines (Mocked Network / Offline)
# ---------------------------------------------------------------------------

def test_indigo_fixture_extraction():
    html = read_fixture("indigo_results.html")
    dep_date = datetime.date(2026, 9, 16)
    quotes = extract_indigo_quotes_from_dom_or_html(
        html_text=html,
        origin="DEL",
        destination="BOM",
        departure_date=dep_date,
        lead_time_days=7,
    )

    assert len(quotes) == 3
    # Flight 1
    q1 = quotes[0]
    assert q1["carrier"] == "IndiGo"
    assert q1["flight_number"] == "6E-205"
    assert q1["fare_class"] == "Saver"
    assert q1["total_fare"] == 5450.0
    assert q1["base_fare"] == 4200.0
    assert q1["taxes"] == 750.0
    assert q1["seats_remaining"] == 4
    assert q1["availability_status"] == "AVAILABLE"

    # Flight 2 (Seats remaining alert)
    q2 = quotes[1]
    assert q2["flight_number"] == "6E-531"
    assert q2["fare_class"] == "Flexi Plus"
    assert q2["total_fare"] == 6890.0
    assert q2["seats_remaining"] == 2
    assert q2["availability_status"] == "AVAILABLE"

    # Flight 3 (Sold out)
    q3 = quotes[2]
    assert q3["flight_number"] == "6E-882"
    assert q3["availability_status"] == "SOLD_OUT"
    assert q3["total_fare"] == 0.0


def test_air_india_fixture_extraction():
    html = read_fixture("air_india_results.html")
    dep_date = datetime.date(2026, 9, 16)
    quotes = extract_air_india_quotes_from_dom_or_html(
        html_text=html,
        origin="DEL",
        destination="BOM",
        departure_date=dep_date,
        lead_time_days=7,
    )

    assert len(quotes) == 3
    q1 = quotes[0]
    assert q1["carrier"] == "Air India"
    assert q1["flight_number"] == "AI-805"
    assert q1["fare_class"] == "Comfort"
    assert q1["total_fare"] == 5820.0
    assert q1["base_fare"] == 4500.0
    assert q1["taxes"] == 820.0
    assert q1["seats_remaining"] == 3
    assert q1["availability_status"] == "AVAILABLE"

    q2 = quotes[1]
    assert q2["flight_number"] == "AI-887"
    assert q2["fare_class"] == "Comfort Plus"
    assert q2["total_fare"] == 7450.0

    q3 = quotes[2]
    assert q3["flight_number"] == "AI-506"
    assert q3["availability_status"] == "SOLD_OUT"


def test_air_india_express_fixture_extraction():
    html = read_fixture("air_india_express_results.html")
    dep_date = datetime.date(2026, 9, 16)
    quotes = extract_air_india_express_quotes_from_dom_or_html(
        html_text=html,
        origin="DEL",
        destination="BOM",
        departure_date=dep_date,
        lead_time_days=7,
    )

    assert len(quotes) == 3
    q1 = quotes[0]
    assert q1["carrier"] == "Air India Express"
    assert q1["flight_number"] == "IX-1132"
    assert q1["fare_class"] == "Xpress Lite"
    assert q1["total_fare"] == 4990.0
    assert q1["base_fare"] == 3900.0
    assert q1["taxes"] == 690.0
    assert q1["seats_remaining"] == 5
    assert q1["availability_status"] == "AVAILABLE"

    q2 = quotes[1]
    assert q2["flight_number"] == "IX-742"
    assert q2["fare_class"] == "Xpress Value"
    assert q2["total_fare"] == 5650.0

    q3 = quotes[2]
    assert q3["flight_number"] == "IX-235"
    assert q3["availability_status"] == "SOLD_OUT"


def test_akasa_fixture_extraction():
    html = read_fixture("akasa_results.html")
    dep_date = datetime.date(2026, 9, 16)
    quotes = extract_akasa_quotes_from_dom_or_html(
        html_text=html,
        origin="DEL",
        destination="BOM",
        departure_date=dep_date,
        lead_time_days=7,
    )

    assert len(quotes) == 3
    q1 = quotes[0]
    assert q1["carrier"] == "Akasa Air"
    assert q1["flight_number"] == "QP-1102"
    assert q1["fare_class"] == "Saver"
    assert q1["total_fare"] == 5320.0
    assert q1["base_fare"] == 4100.0
    assert q1["taxes"] == 720.0
    assert q1["seats_remaining"] == 4
    assert q1["availability_status"] == "AVAILABLE"

    q2 = quotes[1]
    assert q2["flight_number"] == "QP-1355"
    assert q2["fare_class"] == "Flexi"
    assert q2["total_fare"] == 6400.0

    q3 = quotes[2]
    assert q3["flight_number"] == "QP-1406"
    assert q3["availability_status"] == "SOLD_OUT"


def test_spicejet_fixture_extraction():
    html = read_fixture("spicejet_results.html")
    dep_date = datetime.date(2026, 9, 16)
    quotes = extract_spicejet_quotes_from_dom_or_html(
        html_text=html,
        origin="DEL",
        destination="BOM",
        departure_date=dep_date,
        lead_time_days=7,
    )

    assert len(quotes) == 3
    q1 = quotes[0]
    assert q1["carrier"] == "SpiceJet"
    assert q1["flight_number"] == "SG-8169"
    assert q1["fare_class"] == "Spicesaver"
    assert q1["total_fare"] == 4890.0
    assert q1["base_fare"] == 3850.0
    assert q1["taxes"] == 680.0
    assert q1["seats_remaining"] == 2
    assert q1["availability_status"] == "AVAILABLE"

    q2 = quotes[1]
    assert q2["flight_number"] == "SG-253"
    assert q2["fare_class"] == "SpiceMax"
    assert q2["total_fare"] == 6950.0

    q3 = quotes[2]
    assert q3["flight_number"] == "SG-8721"
    assert q3["availability_status"] == "SOLD_OUT"


# ---------------------------------------------------------------------------
# 2. Fare Decomposition Heuristics Tests
# ---------------------------------------------------------------------------

def test_fare_decomposition_heuristics():
    total_fare = 5499.0
    decomp = decompose_fare(total_fare=total_fare, origin="DEL", destination="BOM", fare_class="Economy")

    assert decomp["total_fare"] == total_fare
    assert decomp["base_fare"] > 0
    assert decomp["taxes"] > 0
    assert decomp["fuel_surcharge"] > 0
    assert decomp["airport_fee"] > 0
    assert decomp["user_development_fee"] > 0
    assert decomp["convenience_fee"] > 0
    assert decomp["other_fee"] > 0

    reconstructed_sum = round(
        decomp["base_fare"]
        + decomp["taxes"]
        + decomp["fuel_surcharge"]
        + decomp["airport_fee"]
        + decomp["user_development_fee"]
        + decomp["convenience_fee"]
        + decomp["other_fee"],
        2,
    )
    assert reconstructed_sum == total_fare


def test_fare_decomposition_fallback_in_base_scraper():
    scraper = IndigoScraper(demo_mode=True)
    raw_quote = {
        "origin": "DEL",
        "destination": "BOM",
        "carrier": "IndiGo",
        "total_fare": 6500.0,
        "base_fare": 0.0,
        "taxes": 0.0,
        "fuel_surcharge": 0.0,
    }
    decomposed = scraper.apply_fare_decomposition_if_needed(raw_quote)

    assert decomposed["base_fare"] > 0
    assert decomposed["taxes"] > 0
    assert decomposed["fuel_surcharge"] > 0
    assert decomposed["total_fare"] == 6500.0


# ---------------------------------------------------------------------------
# 3. Robots.txt and Rate Limiter Compliance Tests
# ---------------------------------------------------------------------------

def test_robots_check_allowed_and_cached():
    with patch("urllib.robotparser.RobotFileParser.read") as mock_read, \
         patch("urllib.robotparser.RobotFileParser.can_fetch", return_value=True):
        allowed = is_allowed("https://www.goindigo.in/booking")
        assert allowed is True


def test_robots_check_disallowed():
    with patch("urllib.robotparser.RobotFileParser.read"), \
         patch("urllib.robotparser.RobotFileParser.can_fetch", return_value=False):
        # Clear cache for isolated test
        RobotsChecker._parsers.clear()
        allowed = is_allowed("https://www.disallowed-airline.com/booking")
        assert allowed is False


@pytest.mark.asyncio
async def test_rate_limiter_acquires_delay():
    limiter = RateLimiter(min_delay=0.01, max_delay=0.05)
    wait1 = await limiter.acquire_async("https://www.goindigo.in")
    assert wait1 == 0.0  # First call has no elapsed wait
    wait2 = await limiter.acquire_async("https://www.goindigo.in")
    assert wait2 >= 0.0


# ---------------------------------------------------------------------------
# 4. Robust Error Handling (CAPTCHA, Timeouts, Missing Selectors)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_captcha_page_detection_and_safe_exit():
    scraper = IndigoScraper(demo_mode=False)

    # Mock Page with Cloudflare Turnstile CAPTCHA text
    mock_page = AsyncMock()
    mock_page.title.return_value = "Just a moment... | Attention Required! | Cloudflare"
    mock_page.content.return_value = "<html><body><div class='cf-turnstile'>Verify you are human</div></body></html>"

    captcha_detected = await scraper.detect_captcha_or_block(mock_page)
    assert captcha_detected is not None
    assert "cf-turnstile" in captcha_detected or "verify you are human" in captcha_detected


@pytest.mark.asyncio
async def test_run_query_safely_handles_timeout():
    scraper = IndigoScraper(demo_mode=False)
    mock_page = AsyncMock()

    # Simulate timeout on extract_fares
    with patch.object(scraper, "extract_fares", side_effect=asyncio.TimeoutError("Timeout")):
        with patch("scraper.common.base_scraper.is_allowed", return_value=True), \
             patch("scraper.common.base_scraper.limit_rate", return_value=0.0):
            result = await scraper.run_query(
                page=mock_page,
                origin="DEL",
                destination="BOM",
                departure_date=datetime.date.today(),
                lead_time_days=7,
            )
            # Must return empty list and NOT crash
            assert result == []


@pytest.mark.asyncio
async def test_run_query_safely_handles_unexpected_exception():
    scraper = AirIndiaScraper(demo_mode=False)
    mock_page = AsyncMock()

    with patch.object(scraper, "extract_fares", side_effect=RuntimeError("DOM parsing broken")):
        with patch("scraper.common.base_scraper.is_allowed", return_value=True), \
             patch("scraper.common.base_scraper.limit_rate", return_value=0.0):
            result = await scraper.run_query(
                page=mock_page,
                origin="DEL",
                destination="BOM",
                departure_date=datetime.date.today(),
                lead_time_days=7,
            )
            assert result == []


# ---------------------------------------------------------------------------
# 5. Demo Mode and Database Persistence Tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_demo_mode_persists_to_db():
    scraper = AkasaScraper(demo_mode=True)
    custom_routes = [{"origin": "DEL", "destination": "BOM", "route_code": "DEL-BOM"}]

    quotes = await scraper.run(selected_routes=custom_routes, selected_windows=[7])
    assert len(quotes) > 0

    session = get_session()
    try:
        saved = session.query(FareQuote).filter(
            FareQuote.source == "akasa",
            FareQuote.origin == "DEL",
            FareQuote.destination == "BOM",
        ).all()
        assert len(saved) >= len(quotes)
        last = saved[-1]
        assert last.source == "akasa"
        assert last.source_type == "airline_direct"
        assert last.carrier == "Akasa Air"
        assert last.raw_hash is not None
    finally:
        session.close()


def test_seed_mock_data_for_all_five_airlines():
    today = datetime.date.today()
    airlines = ["indigo", "air_india", "air_india_express", "akasa", "spicejet"]
    for a in airlines:
        quotes = seed_mock_data.generate_airline_mock_quotes(
            airline=a,
            origin="DEL",
            destination="BLR",
            departure_date=today + datetime.timedelta(days=7),
            lead_time_days=7,
        )
        assert len(quotes) >= 3
        for q in quotes:
            assert q["source"] == a
            assert q["source_type"] == "airline_direct"
            assert q["origin"] == "DEL"
            assert q["destination"] == "BLR"
            assert "raw_hash" in q
            assert q["total_fare"] >= 0
