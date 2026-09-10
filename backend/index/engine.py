"""
APIx Index Calculation Engine
Implements the transparent, Laspeyres-type weighted Airfare Price Index (APIx) methodology.
"""

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional
from collections import defaultdict
from sqlalchemy.orm import Session
from backend.models.db_models import (
    FareObservationClean, IndexValue, IndexWeight, Route
)
from backend.config import INITIAL_ROUTES

class APIxIndexEngine:
    """
    Computes real-time, daily, weekly, and monthly APIx values.
    
    Formula:
    1. For each route r and date t:
       P_{r, t} = Average(clean airfares on route r at date t)
    2. Price Relative for route r:
       PR_{r, t} = (P_{r, t} / P_{r, t0}) * 100
       where t0 is the designated base period.
    3. Composite APIx:
       APIx_t = SUM(W_r * PR_{r, t})
       where W_r is the DGCA traffic-based passenger weight (SUM(W_r) = 1.0).
    """

    def __init__(self, db: Session):
        self.db = db

    def get_route_weights(self) -> Dict[str, float]:
        """Loads active route weights from database, normalized to 1.0"""
        db_routes = self.db.query(Route).filter(Route.is_active == True).all()
        if not db_routes:
            return {r["route_code"]: r["weight"] for r in INITIAL_ROUTES}

        raw_weights = {r.route_code: r.weight for r in db_routes}
        total_weight = sum(raw_weights.values())
        if total_weight <= 0:
            total_weight = 1.0
        # Ensure sum == 1.0
        return {r: w / total_weight for r, w in raw_weights.items()}

    def compute_base_period_fares(self, base_date: date) -> Dict[str, float]:
        """
        Computes the benchmark average fare P_{r, t0} for each route during the base period.
        If no quotes exist on base_date, expands to a +/- 3 day window.
        """
        fares = (
            self.db.query(FareObservationClean.route, FareObservationClean.total_fare)
            .filter(FareObservationClean.search_date == base_date)
            .all()
        )

        # Fallback window if exact date has few quotes
        if len(fares) < 20:
            window_start = base_date - timedelta(days=3)
            window_end = base_date + timedelta(days=3)
            fares = (
                self.db.query(FareObservationClean.route, FareObservationClean.total_fare)
                .filter(FareObservationClean.search_date >= window_start)
                .filter(FareObservationClean.search_date <= window_end)
                .all()
            )

        route_sums = defaultdict(list)
        for r_code, fare in fares:
            route_sums[r_code].append(fare)

        base_fares = {}
        for r_code, fare_list in route_sums.items():
            base_fares[r_code] = sum(fare_list) / len(fare_list)

        # Fallback benchmark for routes with missing base quotes
        for r in INITIAL_ROUTES:
            r_code = r["route_code"]
            if r_code not in base_fares:
                base_fares[r_code] = 5200.0

        return base_fares

    def calculate_daily_index(
        self,
        target_date: date,
        base_date: date,
        persist: bool = True
    ) -> Dict[str, Any]:
        """
        Calculates the APIx for a specific target_date relative to base_date.
        """
        route_weights = self.get_route_weights()
        base_fares = self.compute_base_period_fares(base_date)

        # Retrieve clean quotes for target date
        quotes = (
            self.db.query(FareObservationClean.route, FareObservationClean.total_fare)
            .filter(FareObservationClean.search_date == target_date)
            .all()
        )

        route_quotes = defaultdict(list)
        for r_code, fare in quotes:
            route_quotes[r_code].append(fare)

        # Calculate current weighted fare and individual route price relatives
        weighted_fare_sum = 0.0
        base_weighted_fare_sum = 0.0
        route_relatives = {}
        route_current_averages = {}
        total_obs = len(quotes)

        for r_code, weight in route_weights.items():
            current_fare_list = route_quotes.get(r_code, [])
            base_fare = base_fares.get(r_code, 5200.0)

            if current_fare_list:
                curr_avg = sum(current_fare_list) / len(current_fare_list)
            else:
                curr_avg = base_fare  # Impute base fare if no quotes for this route

            price_relative = (curr_avg / base_fare) * 100.0
            route_relatives[r_code] = price_relative
            route_current_averages[r_code] = curr_avg

            weighted_fare_sum += weight * curr_avg
            base_weighted_fare_sum += weight * base_fare

        # Composite APIx = SUM(W_r * PR_{r, t})
        composite_apix = sum(route_weights[r] * route_relatives[r] for r in route_weights)
        overall_price_relative = (weighted_fare_sum / (base_weighted_fare_sum or 1.0)) * 100.0

        result = {
            "index_date": target_date,
            "frequency": "DAILY",
            "apix_value": round(composite_apix, 2),
            "base_period_fare": round(base_weighted_fare_sum, 2),
            "current_weighted_fare": round(weighted_fare_sum, 2),
            "price_relative": round(overall_price_relative, 2),
            "observation_count": total_obs,
            "route_relatives": {k: round(v, 2) for k, v in route_relatives.items()},
            "route_averages": {k: round(v, 2) for k, v in route_current_averages.items()},
            "weights_used": route_weights,
            "calculated_at": datetime.utcnow()
        }

        if persist:
            existing = (
                self.db.query(IndexValue)
                .filter(IndexValue.index_date == target_date)
                .filter(IndexValue.frequency == "DAILY")
                .first()
            )
            if existing:
                existing.apix_value = result["apix_value"]
                existing.base_period_fare = result["base_period_fare"]
                existing.current_weighted_fare = result["current_weighted_fare"]
                existing.price_relative = result["price_relative"]
                existing.observation_count = result["observation_count"]
                existing.calculated_at = result["calculated_at"]
            else:
                db_record = IndexValue(
                    index_date=target_date,
                    frequency="DAILY",
                    apix_value=result["apix_value"],
                    base_period_fare=result["base_period_fare"],
                    current_weighted_fare=result["current_weighted_fare"],
                    price_relative=result["price_relative"],
                    observation_count=result["observation_count"],
                    calculated_at=result["calculated_at"]
                )
                self.db.add(db_record)
            self.db.commit()

        return result

    def compute_all_historical_indices(self, start_date: date, end_date: date, base_date: date):
        """Precomputes and stores daily indices across the entire historical window"""
        curr = start_date
        while curr <= end_date:
            self.calculate_daily_index(curr, base_date=base_date, persist=True)
            curr += timedelta(days=1)
