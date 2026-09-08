"""Airline-specific mock data generator for offline demonstration and testing.
Provides realistic flight schedules, accurate IATA numbering conventions,
fare bucket breakdowns, seats-remaining counts, and sold-out states.
"""
import argparse
import datetime
import hashlib
import math
import random
from typing import Any, Dict, List, Optional

AIRLINE_CONFIGS = {
    "indigo": {
        "carrier_name": "IndiGo",
        "carrier_code": "6E",
        "source_id": "indigo",
        "flight_prefix": "6E",
        "flight_range": (101, 899),
        "fare_classes": ["Saver", "Flexi Plus", "Super 6E"],
        "base_multiplier": 1.00,
        "flight_frequency": 5,
    },
    "air_india": {
        "carrier_name": "Air India",
        "carrier_code": "AI",
        "source_id": "air_india",
        "flight_prefix": "AI",
        "flight_range": (401, 999),
        "fare_classes": ["Comfort", "Comfort Plus", "Flex"],
        "base_multiplier": 1.15,
        "flight_frequency": 4,
    },
    "air_india_express": {
        "carrier_name": "Air India Express",
        "carrier_code": "IX",
        "source_id": "air_india_express",
        "flight_prefix": "IX",
        "flight_range": (1100, 1999),
        "fare_classes": ["Xpress Lite", "Xpress Value", "Xpress Flex"],
        "base_multiplier": 0.90,
        "flight_frequency": 3,
    },
    "akasa": {
        "carrier_name": "Akasa Air",
        "carrier_code": "QP",
        "source_id": "akasa",
        "flight_prefix": "QP",
        "flight_range": (1101, 1699),
        "fare_classes": ["Saver", "Flexi"],
        "base_multiplier": 0.94,
        "flight_frequency": 3,
    },
    "spicejet": {
        "carrier_name": "SpiceJet",
        "carrier_code": "SG",
        "source_id": "spicejet",
        "flight_prefix": "SG",
        "flight_range": (101, 8899),
        "fare_classes": ["Spicesaver", "SpiceMax"],
        "base_multiplier": 0.92,
        "flight_frequency": 3,
    },
}

# Base benchmark prices for domestic routes (Economy baseline)
ROUTE_BENCHMARKS = {
    "DEL-BOM": 4800.0,
    "DEL-BLR": 5400.0,
    "BOM-BLR": 3800.0,
    "DEL-CCU": 4600.0,
    "BLR-HYD": 2900.0,
    "MAA-DEL": 5100.0,
    "CCU-BLR": 5200.0,
    "DEL-HYD": 4200.0,
    "BOM-DEL": 4700.0,
    "BLR-MAA": 2600.0,
}


def generate_airline_mock_quotes(
    airline: str,
    origin: str,
    destination: str,
    departure_date: datetime.date,
    lead_time_days: int = 1,
    seed: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Generate deterministic or randomized mock quotes for a specific airline."""
    key = airline.lower().replace(" ", "_").replace("-", "_")
    cfg = AIRLINE_CONFIGS.get(key)
    if not cfg:
        for k, v in AIRLINE_CONFIGS.items():
            if v["carrier_name"].lower() == airline.lower() or v["carrier_code"].lower() == airline.lower():
                cfg = v
                key = k
                break
    if not cfg:
        cfg = AIRLINE_CONFIGS["indigo"]
        key = "indigo"

    rng = random.Random()
    if seed is not None:
        rng.seed(seed)
    else:
        # Pseudo-deterministic based on date + route + airline for consistency
        route_hash = hash(f"{key}-{origin}-{destination}-{departure_date.isoformat()}-{lead_time_days}")
        rng.seed(abs(route_hash) % (2**31))

    route_code = f"{origin.upper()}-{destination.upper()}"
    base_benchmark = ROUTE_BENCHMARKS.get(route_code, 4500.0)

    # Lead time dynamic pricing: T+1 has surge multiplier, T+45 has early bird discount
    lead_mult = 1.0 + 1.25 * math.exp(-0.065 * lead_time_days)

    obs_timestamp = datetime.datetime.now(datetime.timezone.utc)
    quotes = []

    count = cfg["flight_frequency"]
    min_flt, max_flt = cfg["flight_range"]

    for i in range(count):
        flight_num = f"{cfg['flight_prefix']}-{rng.randint(min_flt, max_flt)}"

        # 5% chance of being sold out on short lead times (T+1)
        is_sold_out = (lead_time_days <= 1) and (rng.random() < 0.12)
        status = "SOLD_OUT" if is_sold_out else "AVAILABLE"

        # Seats remaining indicator (e.g. "Only 2 seats left at this price")
        seats_remaining = None
        if not is_sold_out and rng.random() < 0.40:
            seats_remaining = rng.randint(1, 6)

        # Fare classes
        primary_class = cfg["fare_classes"][0]
        class_mult = 1.0
        if rng.random() > 0.65 and len(cfg["fare_classes"]) > 1:
            primary_class = cfg["fare_classes"][1]
            class_mult = 1.25

        random_noise = rng.uniform(0.95, 1.06)
        total_fare_calc = round(base_benchmark * lead_mult * cfg["base_multiplier"] * class_mult * random_noise, 2)

        # Statutory and component breakdowns
        convenience_fee = 250.0
        udf = 250.0
        airport_fee = 150.0
        other_fee = 50.0
        fixed_sum = convenience_fee + udf + airport_fee + other_fee

        variable_part = max(total_fare_calc - fixed_sum, 1000.0)
        # GST 5%
        taxable_sum = round(variable_part / 1.05, 2)
        taxes = round(variable_part - taxable_sum, 2)
        fuel_surcharge = round(taxable_sum * 0.16, 2)
        base_fare = round(taxable_sum - fuel_surcharge, 2)

        total_fare = round(base_fare + taxes + airport_fee + fuel_surcharge + udf + convenience_fee + other_fee, 2)

        payload = f"{origin}|{destination}|{departure_date.isoformat()}|{cfg['carrier_name']}|{flight_num}|{primary_class}|{cfg['source_id']}|{obs_timestamp.isoformat()}"
        raw_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        quote = {
            "observation_timestamp": obs_timestamp,
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departure_date": departure_date,
            "lead_time_days": lead_time_days,
            "carrier": cfg["carrier_name"],
            "flight_number": flight_num,
            "fare_class": primary_class,
            "base_fare": base_fare if not is_sold_out else 0.0,
            "taxes": taxes if not is_sold_out else 0.0,
            "airport_fee": airport_fee if not is_sold_out else 0.0,
            "fuel_surcharge": fuel_surcharge if not is_sold_out else 0.0,
            "user_development_fee": udf if not is_sold_out else 0.0,
            "convenience_fee": convenience_fee if not is_sold_out else 0.0,
            "other_fee": other_fee if not is_sold_out else 0.0,
            "total_fare": total_fare if not is_sold_out else 0.0,
            "currency": "INR",
            "source": cfg["source_id"],
            "source_type": "airline_direct",
            "source_url": f"https://mock.{cfg['source_id']}.com/search?from={origin}&to={destination}&date={departure_date.isoformat()}",
            "availability_status": status,
            "collection_status": "VALID",
            "seats_remaining": seats_remaining,
            "raw_hash": raw_hash,
            "created_at": obs_timestamp,
        }
        quotes.append(quote)

    return quotes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Airline mock fare generator for AirFareX demo mode")
    parser.add_argument("--airline", default="indigo", choices=list(AIRLINE_CONFIGS.keys()), help="Airline to simulate")
    parser.add_argument("--origin", default="DEL", help="Origin airport code")
    parser.add_argument("--destination", default="BOM", help="Destination airport code")
    parser.add_argument("--advance", type=int, default=7, help="Advance purchase days lead time")
    parser.add_argument("--save", action="store_true", help="Save quotes to database")
    args = parser.parse_args()

    dep = datetime.date.today() + datetime.timedelta(days=args.advance)
    quotes = generate_airline_mock_quotes(
        airline=args.airline,
        origin=args.origin,
        destination=args.destination,
        departure_date=dep,
        lead_time_days=args.advance,
    )

    print(f"Generated {len(quotes)} quotes for {args.airline.upper()} ({args.origin}->{args.destination}, dep: {dep}):")
    for q in quotes:
        print(f"  {q['flight_number']} | {q['fare_class']} | Total: INR {q['total_fare']} | Status: {q['availability_status']} (Seats left: {q['seats_remaining']})")

    if args.save:
        from database.models import save_fare_quote
        for q in quotes:
            save_fare_quote(q)
        print(f"Saved {len(quotes)} quotes to database.")
