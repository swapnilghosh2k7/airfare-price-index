import re
from typing import Dict, Any

class Normalizer:
    AIRPORT_ALIASES = {
        "DELHI": "DEL",
        "MUMBAI": "BOM",
        "BENGALURU": "BLR",
        "BANGALORE": "BLR",
        "KOLKATA": "CCU",
        "HYDERABAD": "HYD",
        "CHENNAI": "MAA",
    }
    
    CARRIER_ALIASES = {
        "6E": "IndiGo",
        "INDIGO": "IndiGo",
        "AI": "Air India",
        "AIRINDIA": "Air India",
        "AIR INDIA": "Air India",
        "UK": "Vistara",
        "VISTARA": "Vistara",
        "QP": "Akasa Air",
        "AKASA": "Akasa Air",
        "AKASA AIR": "Akasa Air",
        "SG": "SpiceJet",
        "SPICEJET": "SpiceJet",
    }

    @classmethod
    def normalize_airport(cls, code_or_city: str) -> str:
        if not code_or_city:
            return ""
        val = str(code_or_city).strip().upper()
        return cls.AIRPORT_ALIASES.get(val, val[:3])

    @classmethod
    def normalize_carrier(cls, carrier_str: str) -> str:
        if not carrier_str:
            return "Unknown"
        val = str(carrier_str).strip().upper()
        return cls.CARRIER_ALIASES.get(val, str(carrier_str).strip())

    @classmethod
    def normalize_currency(cls, curr: str) -> str:
        if not curr:
            return "INR"
        val = str(curr).strip().upper()
        if val in ["₹", "RS", "RUPEES", "INR"]:
            return "INR"
        return val

    @classmethod
    def process_quote_dict(cls, raw: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize a dictionary representation of a fare quote"""
        quote = raw.copy()
        
        quote["origin"] = cls.normalize_airport(quote.get("origin", ""))
        quote["destination"] = cls.normalize_airport(quote.get("destination", ""))
        quote["carrier"] = cls.normalize_carrier(quote.get("carrier", ""))
        quote["currency"] = cls.normalize_currency(quote.get("currency", "INR"))
        
        # Ensure numerical components
        base_fare = float(quote.get("base_fare", 0.0) or 0.0)
        taxes = float(quote.get("taxes", 0.0) or 0.0)
        airport_fee = float(quote.get("airport_fee", 0.0) or 0.0)
        fuel_surcharge = float(quote.get("fuel_surcharge", 0.0) or 0.0)
        user_dev = float(quote.get("user_development_fee", 0.0) or 0.0)
        convenience = float(quote.get("convenience_fee", 0.0) or 0.0)
        other_fee = float(quote.get("other_fee", 0.0) or 0.0)
        
        reconstructed_total = round(
            base_fare + taxes + airport_fee + fuel_surcharge + user_dev + convenience + other_fee, 2
        )
        
        reported_total = float(quote.get("total_fare", 0.0) or 0.0)
        
        # Reconstruct total fare if reported total is missing or 0
        if reported_total <= 0.0 and reconstructed_total > 0.0:
            quote["total_fare"] = reconstructed_total
        else:
            quote["total_fare"] = reported_total
            
        quote["reconstructed_total"] = reconstructed_total
        return quote
