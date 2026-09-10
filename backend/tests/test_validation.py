"""
Automated Tests: Validation and Schema Integrity
"""

import pytest
from datetime import date, timedelta
from backend.synthetic.generator import generate_single_fare_quote
from backend.config import INITIAL_ROUTES, INITIAL_AIRLINES, INITIAL_SOURCES

def test_single_fare_quote_generation():
    route = INITIAL_ROUTES[0]
    airline = INITIAL_AIRLINES[0]
    source = INITIAL_SOURCES[0]
    today = date.today()

    quote = generate_single_fare_quote(
        route_info=route,
        airline_info=airline,
        source_info=source,
        search_date=today,
        advance_days=7,
        inject_anomaly_chance=0.0
    )

    assert quote["route"] == "DEL-BOM"
    assert quote["airline"] == "IndiGo"
    assert quote["source"] == "IndiGo Portal"
    assert quote["advance_purchase_days"] == 7
    assert quote["travel_date"] == today + timedelta(days=7)
    assert quote["total_fare"] > 1000.0
    assert quote["base_fare"] > 0.0
    assert quote["taxes"] > 0.0

def test_fare_component_breakdown():
    route = INITIAL_ROUTES[0]
    airline = INITIAL_AIRLINES[0]
    source = INITIAL_SOURCES[0]
    today = date.today()

    quote = generate_single_fare_quote(
        route_info=route,
        airline_info=airline,
        source_info=source,
        search_date=today,
        advance_days=15,
        inject_anomaly_chance=0.0
    )

    calculated_sum = (
        quote["base_fare"] +
        quote["fuel_surcharge"] +
        quote["user_development_fee"] +
        quote["airport_fee"] +
        quote["taxes"] +
        quote["convenience_fee"]
    )
    assert abs(calculated_sum - quote["total_fare"]) <= 1.0
