"""Fare decomposition heuristics for Indian domestic air travel.
Used when booking engines display an all-inclusive total fare without exposing
an itemized breakdown of base fare, taxes, fuel surcharges, and airport levies.
"""
from typing import Dict, Any

def decompose_fare(
    total_fare: float,
    origin: str = "",
    destination: str = "",
    fare_class: str = "Economy"
) -> Dict[str, float]:
    """Heuristically decompose an all-inclusive domestic Indian airfare into:
      - base_fare
      - taxes (GST 5% for Economy, 12% for Business/Premium)
      - fuel_surcharge (YQ)
      - airport_fee (PSF)
      - user_development_fee (UDF)
      - convenience_fee
      - other_fee (RCS levy)
      - total_fare
    Guarantees: sum of all components equals total_fare exactly.
    """
    total = round(float(total_fare or 0.0), 2)
    if total <= 0:
        return {
            "base_fare": 0.0,
            "taxes": 0.0,
            "airport_fee": 0.0,
            "fuel_surcharge": 0.0,
            "user_development_fee": 0.0,
            "convenience_fee": 0.0,
            "other_fee": 0.0,
            "total_fare": 0.0,
        }

    is_business = any(k in fare_class.lower() for k in ["business", "first", "club"])
    gst_rate = 0.12 if is_business else 0.05

    # Fixed statutory and airport fees
    convenience_fee = 250.0 if total >= 1500 else 0.0
    udf = 250.0 if total >= 2000 else 100.0
    airport_fee = 150.0 if total >= 2000 else 50.0
    other_fee = 50.0  # Regional Connectivity Scheme (RCS) levy

    fixed_fees = convenience_fee + udf + airport_fee + other_fee

    # Ensure fixed fees don't exceed 35% of total
    if fixed_fees >= 0.35 * total:
        scale = (0.35 * total) / fixed_fees
        convenience_fee = round(convenience_fee * scale, 2)
        udf = round(udf * scale, 2)
        airport_fee = round(airport_fee * scale, 2)
        other_fee = round(other_fee * scale, 2)
        fixed_fees = convenience_fee + udf + airport_fee + other_fee

    variable_amount = total - fixed_fees

    # Taxes apply on (Base Fare + Fuel Surcharge)
    taxable_sum = round(variable_amount / (1.0 + gst_rate), 2)
    taxes = round(variable_amount - taxable_sum, 2)

    # Fuel Surcharge (YQ) is roughly 16% of taxable sum on domestic routes
    fuel_surcharge = round(taxable_sum * 0.16, 2)
    base_fare = round(taxable_sum - fuel_surcharge, 2)

    # Guarantee component equality to total_fare
    current_sum = round(base_fare + taxes + airport_fee + fuel_surcharge + udf + convenience_fee + other_fee, 2)
    delta = round(total - current_sum, 2)
    base_fare = round(base_fare + delta, 2)

    return {
        "base_fare": base_fare,
        "taxes": taxes,
        "airport_fee": airport_fee,
        "fuel_surcharge": fuel_surcharge,
        "user_development_fee": udf,
        "convenience_fee": convenience_fee,
        "other_fee": other_fee,
        "total_fare": total,
    }
