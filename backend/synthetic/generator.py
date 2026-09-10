"""
Realistic Microeconomic Airfare Data Generator for APIx Platform

Models real-world Indian civil aviation pricing dynamics:
- Distance & city-pair baseline costs
- Advance-purchase non-linear yield escalation (T+45 to T+1)
- Airline pricing power (FSC vs LCC)
- Day-of-week demand (weekend surge)
- Time-of-day slots (peak morning/evening vs mid-day)
- Realistic component breakdowns (Base, Fuel Surcharge, UDF, GST, Convenience fee)
- Controllable anomalies (outliers, duplicates, component mismatch) for pipeline demonstration
"""

import math
import random
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from backend.config import INITIAL_ROUTES, INITIAL_AIRLINES, INITIAL_SOURCES, ADVANCE_PURCHASE_WINDOWS

# Route baseline distances (km) and base fare ranges
ROUTE_DISTANCE_MAP = {
    "DEL-BOM": (1140, 4200),
    "BOM-DEL": (1140, 4200),
    "DEL-BLR": (1740, 5200),
    "BLR-DEL": (1740, 5200),
    "BOM-BLR": (840, 3600),
    "BLR-BOM": (840, 3600),
    "DEL-HYD": (1260, 4400),
    "HYD-DEL": (1260, 4400),
    "DEL-CCU": (1305, 4600),
    "CCU-DEL": (1305, 4600),
    "MAA-DEL": (1760, 5300),
    "DEL-MAA": (1760, 5300),
    "BOM-HYD": (620, 3200),
    "HYD-BOM": (620, 3200),
    "BOM-MAA": (1030, 4000),
    "MAA-BOM": (1030, 4000),
    "BLR-HYD": (500, 2900),
    "DEL-PNQ": (1170, 4300),
    "BOM-GOI": (440, 2800),
    "DEL-GOI": (1510, 5000),
}

# Airline pricing factors
AIRLINE_MULTIPLIERS = {
    "IndiGo": 1.00,             # Market reference LCC
    "Air India": 1.20,          # Full Service Carrier (meals, 23kg check-in bag)
    "Air India Express": 0.96,  # Budget subsidiary
    "Akasa Air": 0.94,          # Agresive budget challenger
    "SpiceJet": 0.92,           # Value pricing
}

# Advance purchase window elasticity multipliers
WINDOW_MULTIPLIERS = {
    45: 0.74,   # T+45: Early bird tier, highest availability
    30: 0.84,   # T+30: Advance planning tier
    15: 1.00,   # T+15: Baseline reference pricing
    7: 1.28,    # T+7:  Escalation window, business travelers begin booking
    1: 1.72,    # T+1:  Last-minute distress/premium surge pricing
}

FLIGHT_TIMES = [
    ("06:15", "08:25", "02h 10m", 1.12),  # Peak morning
    ("08:45", "11:00", "02h 15m", 1.08),  # Morning
    ("11:30", "13:45", "02h 15m", 0.92),  # Mid-day
    ("14:20", "16:35", "02h 15m", 0.90),  # Afternoon
    ("17:45", "20:00", "02h 15m", 1.14),  # Peak evening
    ("20:30", "22:45", "02h 15m", 1.05),  # Late evening
    ("22:50", "01:00", "02h 10m", 0.88),  # Red-eye
]

AIRPORT_UDF_FEES = {
    "DEL": 680.0,
    "BOM": 620.0,
    "BLR": 540.0,
    "HYD": 480.0,
    "CCU": 420.0,
    "MAA": 440.0,
    "PNQ": 380.0,
    "GOI": 400.0,
}

def generate_flight_number(iata_code: str) -> str:
    return f"{iata_code}-{random.randint(101, 999)}"

def generate_single_fare_quote(
    route_info: Dict[str, Any],
    airline_info: Dict[str, Any],
    source_info: Dict[str, Any],
    search_date: date,
    advance_days: int,
    scrape_run_id: Optional[str] = None,
    inject_anomaly_chance: float = 0.02
) -> Dict[str, Any]:
    """
    Generates a single realistic Indian domestic airfare observation.
    """
    route_code = route_info["route_code"]
    origin = route_info["origin"]
    destination = route_info["destination"]
    airline_name = airline_info["airline_name"]
    iata_code = airline_info["iata_code"]
    source_name = source_info["source_name"]
    source_type = source_info["source_type"]

    travel_date = search_date + timedelta(days=advance_days)

    # 1. Base cost from route distance
    _, base_route_cost = ROUTE_DISTANCE_MAP.get(route_code, (1000, 4000))

    # 2. Airline tier factor
    airline_factor = AIRLINE_MULTIPLIERS.get(airline_name, 1.0)

    # 3. Advance purchase elasticity factor
    window_factor = WINDOW_MULTIPLIERS.get(advance_days, 1.0)

    # 4. Day of week effect (Friday & Sunday high, Tuesday/Wednesday low)
    weekday = travel_date.weekday()
    if weekday in (4, 6):  # Friday or Sunday
        dow_factor = 1.18
    elif weekday in (1, 2):  # Tuesday or Wednesday
        dow_factor = 0.92
    else:
        dow_factor = 1.00

    # 5. Departure time slot factor
    dep_time, arr_time, duration, time_factor = random.choice(FLIGHT_TIMES)

    # 6. Natural market random noise (+/- 6%)
    noise_factor = 1.0 + random.uniform(-0.06, 0.06)

    # Calculate baseline raw total fare
    calculated_fare = base_route_cost * airline_factor * window_factor * dow_factor * time_factor * noise_factor

    # Disaggregate into realistic Indian airfare components
    # Base fare is roughly 68% of core fare
    base_fare = round(calculated_fare * 0.68, 2)
    fuel_surcharge = round(random.choice([750.0, 850.0, 950.0, 1100.0]), 2)
    
    # User Development Fee (origin airport specific)
    udf = AIRPORT_UDF_FEES.get(origin, 450.0)
    airport_fee = round(random.choice([95.0, 120.0, 150.0]), 2)

    # GST on economy in India is 5% of (Base + Fuel)
    taxes = round((base_fare + fuel_surcharge) * 0.05, 2)

    # Convenience fee (higher on OTAs)
    convenience_fee = round(random.choice([350.0, 400.0, 450.0]) if source_type == "OTA" else 0.0, 2)

    total_fare = round(base_fare + fuel_surcharge + udf + airport_fee + taxes + convenience_fee, 2)

    # Controllable Anomaly Injection for Cleaning Pipeline Demonstration
    anomaly_type = None
    if random.random() < inject_anomaly_chance:
        dice = random.random()
        if dice < 0.35:
            # Outlier fare (e.g. ₹68,000 for standard economy or ₹250)
            total_fare = round(total_fare * random.choice([5.5, 7.0]), 2)
            base_fare = round(total_fare * 0.7, 2)
            anomaly_type = "OUTLIER_SURGE"
        elif dice < 0.70:
            # Component sum mismatch
            base_fare = round(base_fare * 1.4, 2)  # Causes Base+Taxes != Total
            anomaly_type = "COMPONENT_MISMATCH"
        else:
            # Sold out or negative fare
            total_fare = 0.0
            base_fare = 0.0
            anomaly_type = "ZERO_FARE"

    return {
        "search_date": search_date,
        "travel_date": travel_date,
        "origin": origin,
        "destination": destination,
        "route": route_code,
        "airline": airline_name,
        "source": source_name,
        "source_type": source_type,
        "flight_number": generate_flight_number(iata_code),
        "departure_time": dep_time,
        "arrival_time": arr_time,
        "duration": duration,
        "stops": 0,
        "fare_class": "Economy",
        "refundable": (airline_name == "Air India"),
        "base_fare": base_fare,
        "taxes": taxes,
        "airport_fee": airport_fee,
        "user_development_fee": udf,
        "convenience_fee": convenience_fee,
        "fuel_surcharge": fuel_surcharge,
        "total_fare": total_fare,
        "currency": "INR",
        "advance_purchase_days": advance_days,
        "availability_status": "AVAILABLE" if total_fare > 0 else "SOLD_OUT",
        "scrape_status": "SUCCESS",
        "scrape_run_id": scrape_run_id,
        "anomaly_type": anomaly_type
    }

def generate_multi_day_dataset(
    days_back: int = 30,
    routes: Optional[List[Dict[str, Any]]] = None,
    airlines: Optional[List[Dict[str, Any]]] = None,
    sources: Optional[List[Dict[str, Any]]] = None,
    advance_windows: Optional[List[int]] = None,
    quotes_per_window: int = 2
) -> List[Dict[str, Any]]:
    """
    Generates a full 30-day realistic historical airfare dataset across routes, airlines, and advance purchase windows.
    """
    routes = routes or INITIAL_ROUTES
    airlines = airlines or INITIAL_AIRLINES
    sources = sources or INITIAL_SOURCES
    advance_windows = advance_windows or ADVANCE_PURCHASE_WINDOWS

    today = date.today()
    start_date = today - timedelta(days=days_back)

    dataset = []
    
    for day_offset in range(days_back + 1):
        current_date = start_date + timedelta(days=day_offset)
        
        # Macro drift: simulate subtle macro inflation trend (+1.5% over 30 days)
        drift = 1.0 + (day_offset / days_back) * 0.02

        for route in routes:
            for airline in airlines:
                # Find matching source or use primary OTA
                source = next((s for s in sources if airline["airline_name"] in s["source_name"]), sources[0])
                
                for window in advance_windows:
                    for _ in range(quotes_per_window):
                        quote = generate_single_fare_quote(
                            route_info=route,
                            airline_info=airline,
                            source_info=source,
                            search_date=current_date,
                            advance_days=window,
                            inject_anomaly_chance=0.03  # 3% realistic anomalies for data cleaning proof
                        )
                        # Apply subtle macro drift to core fare and re-verify component sum
                        if quote["total_fare"] > 0 and quote.get("anomaly_type") != "COMPONENT_MISMATCH":
                            drift_base = round(quote["base_fare"] * drift, 2)
                            drift_fuel = round(quote["fuel_surcharge"] * drift, 2)
                            drift_taxes = round((drift_base + drift_fuel) * 0.05, 2)
                            quote["base_fare"] = drift_base
                            quote["fuel_surcharge"] = drift_fuel
                            quote["taxes"] = drift_taxes
                            quote["total_fare"] = round(
                                drift_base + drift_fuel + quote["taxes"] + quote["user_development_fee"] +
                                quote["airport_fee"] + quote["convenience_fee"], 2
                            )
                        
                        dataset.append(quote)

    return dataset
