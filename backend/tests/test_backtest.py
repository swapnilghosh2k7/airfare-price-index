"""
Automated Tests: Backtesting and DGCA Statistical Metrics
"""

from datetime import date, timedelta
from backend.database import SessionLocal
from backend.backtest.engine import BacktestEngine

def test_backtest_metric_calculations():
    db = SessionLocal()
    try:
        engine = BacktestEngine(db)
        today = date.today()
        res = engine.run_backtest(start_date=today - timedelta(days=15), end_date=today, is_synthetic=True)

        assert "mae" in res
        assert "mape" in res
        assert "rmse" in res
        assert "correlation" in res
        assert "bias" in res
        assert res["sample_size"] > 0
        assert res["mae"] >= 0.0
        assert res["mape"] >= 0.0
        assert res["rmse"] >= 0.0
        assert -1.0 <= res["correlation"] <= 1.0
    finally:
        db.close()
