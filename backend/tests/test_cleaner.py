"""
Automated Tests: Data Cleaning Pipeline
"""

from datetime import date, timedelta
from backend.pipeline.cleaner import DataCleaningPipeline
from backend.config import INITIAL_ROUTES, INITIAL_AIRLINES, INITIAL_SOURCES
from backend.synthetic.generator import generate_single_fare_quote

def test_cleaner_accepts_valid_quote():
    cleaner = DataCleaningPipeline()
    today = date.today()
    quote = generate_single_fare_quote(
        INITIAL_ROUTES[0], INITIAL_AIRLINES[0], INITIAL_SOURCES[0],
        search_date=today, advance_days=15, inject_anomaly_chance=0.0
    )

    clean_quotes, rejected_quotes = cleaner.clean_batch([quote])
    assert len(clean_quotes) == 1
    assert len(rejected_quotes) == 0
    assert clean_quotes[0]["route"] == "DEL-BOM"

def test_cleaner_rejects_component_mismatch():
    cleaner = DataCleaningPipeline()
    today = date.today()
    quote = generate_single_fare_quote(
        INITIAL_ROUTES[0], INITIAL_AIRLINES[0], INITIAL_SOURCES[0],
        search_date=today, advance_days=15, inject_anomaly_chance=0.0
    )
    quote["base_fare"] += 2000.0  # Causes sum to mismatch total_fare

    clean_quotes, rejected_quotes = cleaner.clean_batch([quote])
    assert len(clean_quotes) == 0
    assert len(rejected_quotes) == 1
    assert rejected_quotes[0]["rejection_reason"] == "FARE_COMPONENT_SUM_MISMATCH"

def test_cleaner_rejects_duplicate():
    cleaner = DataCleaningPipeline()
    today = date.today()
    q1 = generate_single_fare_quote(
        INITIAL_ROUTES[0], INITIAL_AIRLINES[0], INITIAL_SOURCES[0],
        search_date=today, advance_days=15, inject_anomaly_chance=0.0
    )
    q2 = dict(q1)  # Exact duplicate

    clean_quotes, rejected_quotes = cleaner.clean_batch([q1, q2])
    assert len(clean_quotes) == 1
    assert len(rejected_quotes) == 1
    assert rejected_quotes[0]["rejection_reason"] == "DUPLICATE_QUOTE"

def test_cleaner_rejects_invalid_currency():
    cleaner = DataCleaningPipeline()
    today = date.today()
    quote = generate_single_fare_quote(
        INITIAL_ROUTES[0], INITIAL_AIRLINES[0], INITIAL_SOURCES[0],
        search_date=today, advance_days=15, inject_anomaly_chance=0.0
    )
    quote["currency"] = "USD"

    clean_quotes, rejected_quotes = cleaner.clean_batch([quote])
    assert len(clean_quotes) == 0
    assert len(rejected_quotes) == 1
    assert rejected_quotes[0]["rejection_reason"] == "INVALID_CURRENCY"
