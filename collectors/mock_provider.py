import random
import math
import hashlib
from datetime import date, datetime
from typing import List, Dict, Any
from collectors.base_provider import FareProvider

class MockFareProvider(FareProvider):
    @property
    def provider_id(self) -> str:
        return "mock_provider"

    @property
    def provider_name(self) -> str:
        return "Synthetic Airfare Quote Generator"

    async def search_fares(
        self,
        origin: str,
        destination: str,
        departure_date: date,
        lead_time_days: int = 1
    ) -> List[Dict[str, Any]]:
        obs_dt = datetime.utcnow()
        route_code = f"{origin.upper()}-{destination.upper()}"
        base_price = 4500.0

        carriers = [
            {"name": "IndiGo", "code": "6E", "mult": 1.0},
            {"name": "Air India", "code": "AI", "mult": 1.15},
            {"name": "Akasa Air", "code": "QP", "mult": 0.94},
        ]

        quotes = []
        lead_mult = 1.0 + 1.25 * math.exp(-0.065 * lead_time_days)

        for c in carriers:
            calculated_base = round(base_price * lead_mult * c["mult"] * random.uniform(0.95, 1.05), 2)
            taxes = round(calculated_base * 0.10, 2)
            fuel = round(calculated_base * 0.12, 2)
            airport = 350.0
            conv = 250.0
            total = round(calculated_base + taxes + fuel + airport + conv, 2)

            flight_num = f"{c['code']}-{random.randint(100, 999)}"
            payload = f"{origin}|{destination}|{departure_date}|{c['name']}|{flight_num}|Economy|mock_provider|{obs_dt.isoformat()}"
            raw_hash = hashlib.sha256(payload.encode("utf-8")).hexdigest()

            quotes.append({
                "observation_timestamp": obs_dt.isoformat(),
                "origin": origin.upper(),
                "destination": destination.upper(),
                "departure_date": departure_date.isoformat(),
                "lead_time_days": lead_time_days,
                "carrier": c["name"],
                "flight_number": flight_num,
                "fare_class": "Economy",
                "base_fare": calculated_base,
                "taxes": taxes,
                "airport_fee": airport,
                "fuel_surcharge": fuel,
                "user_development_fee": 200.0,
                "convenience_fee": conv,
                "other_fee": 0.0,
                "total_fare": total,
                "currency": "INR",
                "source": self.provider_id,
                "source_url": f"https://mock.airfarex.local/search?origin={origin}&dest={destination}&date={departure_date.isoformat()}",
                "availability_status": "AVAILABLE",
                "collection_status": "VALID",
                "raw_hash": raw_hash,
                "created_at": datetime.utcnow().isoformat()
            })

        return quotes
