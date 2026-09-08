import pytest
from backend.app.indexing.laspeyres import LaspeyresIndexCalculator

def test_route_index_math():
    # Base = 5000, Current = 6000 -> Index = 120.0
    idx = LaspeyresIndexCalculator.calculate_route_index(p_current=6000.0, p_base=5000.0)
    assert idx == 120.0

    # Base = 4000, Current = 3800 -> Index = 95.0
    idx_lower = LaspeyresIndexCalculator.calculate_route_index(p_current=3800.0, p_base=4000.0)
    assert idx_lower == 95.0

def test_national_index_weighted_math():
    # Route A = 120.0 (weight 0.6), Route B = 110.0 (weight 0.4)
    # Expected APIx = (120*0.6 + 110*0.4) / (0.6 + 0.4) = (72 + 44) / 1.0 = 116.0
    route_indices = {"DEL-BOM": 120.0, "DEL-BLR": 110.0}
    route_weights = {"DEL-BOM": 0.6, "DEL-BLR": 0.4}

    national = LaspeyresIndexCalculator.calculate_national_index(route_indices, route_weights)
    assert national == 116.0

def test_weight_normalization_math():
    # Unnormalized weights: Route A = 120.0 (weight 3.0), Route B = 110.0 (weight 2.0)
    # Normalized weights: 3/5 = 0.6, 2/5 = 0.4 -> Expected APIx = 116.0
    route_indices = {"DEL-BOM": 120.0, "DEL-BLR": 110.0}
    route_weights = {"DEL-BOM": 3.0, "DEL-BLR": 2.0}

    national = LaspeyresIndexCalculator.calculate_national_index(route_indices, route_weights)
    assert national == 116.0
