"""
Automated Tests: APIx Index Calculation
"""

from datetime import date, timedelta
from backend.database import SessionLocal
from backend.index.engine import APIxIndexEngine
from backend.config import BASE_PERIOD_DATE

def test_route_weights_sum_to_one():
    db = SessionLocal()
    try:
        engine = APIxIndexEngine(db)
        weights = engine.get_route_weights()
        total_weight = sum(weights.values())
        assert abs(total_weight - 1.0) < 0.001
        assert len(weights) >= 20
    finally:
        db.close()

def test_index_calculation_for_target_date():
    db = SessionLocal()
    try:
        engine = APIxIndexEngine(db)
        today = date.today()
        base_dt = date.fromisoformat(BASE_PERIOD_DATE)
        res = engine.calculate_daily_index(target_date=today, base_date=base_dt, persist=False)

        assert "apix_value" in res
        assert res["apix_value"] > 50.0 and res["apix_value"] < 250.0
        assert res["current_weighted_fare"] > 1000.0
        assert res["frequency"] == "DAILY"
    finally:
        db.close()
