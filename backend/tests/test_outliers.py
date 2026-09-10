"""
Automated Tests: Statistical Outlier Detection (IQR & MAD)
"""

from backend.pipeline.outliers import (
    compute_iqr_bounds, compute_mad_stats, compute_robust_z_score, detect_outliers_in_stratum
)

def test_compute_iqr_bounds():
    # Normal distribution values around 5000
    fares = [4500.0, 4800.0, 4900.0, 5000.0, 5100.0, 5200.0, 5500.0]
    q1, q3, lower, upper = compute_iqr_bounds(fares, multiplier=1.5)

    assert q1 < q3
    assert lower < q1
    assert upper > q3

def test_mad_and_robust_z_score():
    fares = [4800.0, 4900.0, 5000.0, 5100.0, 5200.0]
    median, mad = compute_mad_stats(fares)
    assert median == 5000.0
    assert mad > 0.0

    # Normal point
    z_normal = compute_robust_z_score(5050.0, median, mad)
    assert abs(z_normal) < 2.0

    # Extreme surge point (e.g. ₹35,000)
    z_outlier = compute_robust_z_score(35000.0, median, mad)
    assert z_outlier > 3.0

def test_detect_outliers_in_stratum():
    observations = [
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 5000.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 5200.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 5100.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 4900.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 5300.0},
        {"route": "DEL-BOM", "advance_purchase_days": 7, "total_fare": 38000.0},  # Extreme outlier
    ]

    clean, outliers = detect_outliers_in_stratum(observations)
    assert len(clean) == 5
    assert len(outliers) == 1
    assert outliers[0]["total_fare"] == 38000.0
    assert outliers[0]["is_outlier"] is True
