import pytest
import pandas as pd
from backend.app.cleaning.normalizer import Normalizer
from backend.app.cleaning.deduplication import Deduplicator
from backend.app.cleaning.outliers import OutlierDetector
from backend.app.cleaning.quality_score import QualityScorer

def test_normalizer():
    assert Normalizer.normalize_airport("MUMBAI") == "BOM"
    assert Normalizer.normalize_airport("delhi") == "DEL"
    assert Normalizer.normalize_carrier("6E") == "IndiGo"
    assert Normalizer.normalize_currency("₹") == "INR"

    raw = {
        "origin": "mumbai",
        "destination": "delhi",
        "carrier": "6E",
        "base_fare": 4000.0,
        "taxes": 400.0,
        "total_fare": 0.0
    }
    proc = Normalizer.process_quote_dict(raw)
    assert proc["origin"] == "BOM"
    assert proc["destination"] == "DEL"
    assert proc["reconstructed_total"] == 4400.0
    assert proc["total_fare"] == 4400.0

def test_deduplicator():
    q1 = {
        "origin": "DEL", "destination": "BOM", "departure_date": "2026-09-10",
        "carrier": "IndiGo", "flight_number": "6E-101", "fare_class": "Economy",
        "source": "mock_provider", "observation_timestamp": "2026-09-03T10:00:00"
    }
    q2 = q1.copy()
    
    res = Deduplicator.flag_duplicates([q1, q2])
    assert res[0]["duplicate_flag"] is False
    assert res[1]["duplicate_flag"] is True

def test_outlier_detector():
    data = {
        "route_code": ["DEL-BOM"] * 10,
        "lead_time_days": [7] * 10,
        "total_fare": [5000.0, 5100.0, 5050.0, 4950.0, 5200.0, 5000.0, 5150.0, 4900.0, 5050.0, 25000.0]
    }
    df = pd.DataFrame(data)
    flagged = OutlierDetector.flag_outliers(df, method="MAD", mad_threshold=3.0)
    assert bool(flagged.iloc[9]["outlier_flag"]) is True
    assert bool(flagged.iloc[0]["outlier_flag"]) is False

def test_quality_scorer():
    q_good = {
        "origin": "DEL", "destination": "BOM", "departure_date": "2026-09-10",
        "carrier": "IndiGo", "total_fare": 5000.0, "reconstructed_total": 5000.0
    }
    score, missing, errors = QualityScorer.evaluate_quote(q_good)
    assert score == 100.0
    assert len(missing) == 0

    q_bad = {
        "origin": "DEL", "destination": "BOM", "departure_date": "2026-09-10",
        "carrier": "IndiGo", "total_fare": 5000.0, "duplicate_flag": True, "outlier_flag": True
    }
    score_bad, missing, errors = QualityScorer.evaluate_quote(q_bad)
    assert score_bad < 100.0
    assert "Duplicate quote detected" in errors
