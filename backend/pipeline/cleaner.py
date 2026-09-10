"""
Automated Data-Cleaning Pipeline for APIx
Implements the 12-step validation, deduplication, component consistency, and outlier filtering process
"""

import json
from datetime import date, datetime
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
from backend.pipeline.outliers import detect_outliers_in_stratum
from backend.config import INITIAL_ROUTES, INITIAL_AIRLINES

VALID_ROUTES = {r["route_code"] for r in INITIAL_ROUTES}
VALID_AIRLINES = {a["airline_name"] for a in INITIAL_AIRLINES}
VALID_CURRENCIES = {"INR", "Rs", "₹"}

class DataCleaningPipeline:
    def __init__(self, iqr_multiplier: float = 1.5, mad_z_threshold: float = 3.0):
        self.iqr_multiplier = iqr_multiplier
        self.mad_z_threshold = mad_z_threshold

    def clean_batch(
        self,
        raw_quotes: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Executes the 12-step data cleaning pipeline on a batch of raw airfare quotes.
        Returns:
            clean_quotes: Validated, normalized observations
            rejected_quotes: Rejected quotes with structured rejection reasons
        """
        candidate_quotes = []
        rejected_quotes = []
        seen_keys = set()

        for quote in raw_quotes:
            # 1. Schema Validation (required fields)
            required_keys = ["route", "airline", "source", "travel_date", "search_date", "total_fare", "base_fare"]
            missing_keys = [k for k in required_keys if k not in quote or quote[k] is None]
            if missing_keys:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "MISSING_REQUIRED_FIELDS",
                    "rejection_details": f"Missing fields: {', '.join(missing_keys)}"
                })
                continue

            # 2. Missing value checks
            if str(quote["route"]).strip() == "" or str(quote["airline"]).strip() == "":
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "EMPTY_ESSENTIAL_VALUE",
                    "rejection_details": "Route or Airline is empty string"
                })
                continue

            # 3. Duplicate Quote Removal (unique key: route, airline, travel_date, flight_number, total_fare)
            unique_key = (
                str(quote.get("route")),
                str(quote.get("airline")),
                str(quote.get("travel_date")),
                str(quote.get("flight_number")),
                round(float(quote.get("total_fare", 0)), 2)
            )
            if unique_key in seen_keys:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "DUPLICATE_QUOTE",
                    "rejection_details": f"Duplicate flight fare signature: {unique_key}"
                })
                continue
            seen_keys.add(unique_key)

            # 4. Currency Validation
            curr = str(quote.get("currency", "INR")).strip()
            if curr not in VALID_CURRENCIES:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "INVALID_CURRENCY",
                    "rejection_details": f"Unsupported currency '{curr}', must be INR"
                })
                continue

            # 5. Route Validation
            route = str(quote.get("route")).strip().upper()
            if route not in VALID_ROUTES:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "INVALID_ROUTE",
                    "rejection_details": f"Route '{route}' is not in domestic basket"
                })
                continue

            # 6. Airline Validation
            airline = str(quote.get("airline")).strip()
            if airline not in VALID_AIRLINES:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "INVALID_AIRLINE",
                    "rejection_details": f"Airline '{airline}' not recognized in fleet registry"
                })
                continue

            # 7. Timestamp / Travel Date Validation
            search_dt = quote.get("search_date")
            travel_dt = quote.get("travel_date")
            if isinstance(search_dt, str):
                search_dt = date.fromisoformat(search_dt)
            if isinstance(travel_dt, str):
                travel_dt = date.fromisoformat(travel_dt)

            if travel_dt < search_dt:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "CHRONOLOGICAL_INCONSISTENCY",
                    "rejection_details": f"Travel date {travel_dt} is before search date {search_dt}"
                })
                continue

            # 8. Sold-out or Cancelled Flight Handling
            avail = str(quote.get("availability_status", "AVAILABLE")).upper()
            total_fare = float(quote.get("total_fare", 0.0))
            if avail == "SOLD_OUT" or total_fare <= 0:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "FLIGHT_SOLD_OUT_OR_ZERO",
                    "rejection_details": f"Availability: {avail}, Fare: {total_fare}"
                })
                continue

            # 9. Negative or Absurdly Low/High Fare Detection
            if total_fare < 500.0 or total_fare > 150000.0:
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "FARE_BOUNDS_VIOLATION",
                    "rejection_details": f"Total fare ₹{total_fare} outside permissible bounds [500, 150000]"
                })
                continue

            # 10. Fare Component Consistency Validation
            base_fare = float(quote.get("base_fare", 0.0))
            taxes = float(quote.get("taxes", 0.0))
            airport_fee = float(quote.get("airport_fee", 0.0))
            udf = float(quote.get("user_development_fee", 0.0))
            convenience = float(quote.get("convenience_fee", 0.0))
            fuel = float(quote.get("fuel_surcharge", 0.0))

            computed_sum = base_fare + taxes + airport_fee + udf + convenience + fuel
            if abs(computed_sum - total_fare) > 2.0:  # Allow small rounding tolerance up to ₹2.0
                rejected_quotes.append({
                    "raw_quote": quote,
                    "rejection_reason": "FARE_COMPONENT_SUM_MISMATCH",
                    "rejection_details": f"Components sum (₹{computed_sum:.2f}) != Total fare (₹{total_fare:.2f})"
                })
                continue

            # 11. Advance window normalization
            computed_advance = (travel_dt - search_dt).days
            quote["advance_purchase_days"] = quote.get("advance_purchase_days") or computed_advance

            # Candidate passed structural rules, proceed to stratified statistical outlier check
            candidate_quotes.append(quote)

        # 12. Stratified Statistical Outlier Detection (Grouped by Route and Advance Window)
        clean_quotes = []
        strata = defaultdict(list)
        for cand in candidate_quotes:
            stratum_key = (cand["route"], cand["advance_purchase_days"])
            strata[stratum_key].append(cand)

        for stratum_key, stratum_quotes in strata.items():
            stratum_clean, stratum_outliers = detect_outliers_in_stratum(
                stratum_quotes,
                iqr_multiplier=self.iqr_multiplier,
                mad_z_threshold=self.mad_z_threshold
            )
            clean_quotes.extend(stratum_clean)
            for outl in stratum_outliers:
                diag = outl.get("outlier_diagnostic", {})
                rejected_quotes.append({
                    "raw_quote": outl,
                    "rejection_reason": "STATISTICAL_OUTLIER",
                    "rejection_details": f"IQR/MAD outlier: z-score={diag.get('z_score')}, median=₹{diag.get('median')}, MAD=₹{diag.get('mad')}"
                })

        return clean_quotes, rejected_quotes
