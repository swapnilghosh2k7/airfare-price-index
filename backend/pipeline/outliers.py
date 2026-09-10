"""
Statistically Defensible Outlier Detection Engine
Implements Interquartile Range (IQR), Median Absolute Deviation (MAD), and Robust Z-Scores
"""

import math
import statistics
from typing import List, Dict, Any, Tuple, Optional

def compute_percentiles(values: List[float], p: float) -> float:
    """Computes empirical percentile p in [0, 1] using standard linear interpolation"""
    if not values:
        return 0.0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    if n == 1:
        return sorted_vals[0]
    
    idx = (n - 1) * p
    lower = int(math.floor(idx))
    upper = int(math.ceil(idx))
    weight = idx - lower
    return sorted_vals[lower] * (1.0 - weight) + sorted_vals[upper] * weight

def compute_iqr_bounds(values: List[float], multiplier: float = 1.5) -> Tuple[float, float, float, float]:
    """
    Computes Q1, Q3, and IQR bounds: [Q1 - 1.5*IQR, Q3 + 1.5*IQR]
    Returns (q1, q3, lower_bound, upper_bound)
    """
    if len(values) < 4:
        # For very small sample sizes, use broad empirical bounds
        if not values:
            return 0.0, 0.0, 0.0, 0.0
        med = statistics.median(values)
        return med * 0.5, med * 1.5, med * 0.3, med * 2.5

    q1 = compute_percentiles(values, 0.25)
    q3 = compute_percentiles(values, 0.75)
    iqr = q3 - q1
    lower_bound = max(500.0, q1 - multiplier * iqr)
    upper_bound = q3 + multiplier * iqr
    return q1, q3, lower_bound, upper_bound

def compute_mad_stats(values: List[float]) -> Tuple[float, float]:
    """
    Computes Median and Median Absolute Deviation (MAD)
    MAD = median(|X_i - median(X)|)
    Returns (median, mad)
    """
    if not values:
        return 0.0, 0.0
    med = statistics.median(values)
    abs_deviations = [abs(x - med) for x in values]
    mad = statistics.median(abs_deviations)
    return med, mad

def compute_robust_z_score(value: float, median: float, mad: float) -> float:
    """
    Computes Boris Iglewicz and David Hoaglin robust Z-score:
    M_i = 0.6745 * (x_i - median) / MAD
    Threshold typically |M_i| > 3.0
    """
    if mad <= 0.0001:
        return 0.0
    return 0.6745 * (value - median) / mad

def detect_outliers_in_stratum(
    observations: List[Dict[str, Any]],
    iqr_multiplier: float = 1.5,
    mad_z_threshold: float = 3.0
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Analyzes a single stratum (e.g. DEL-BOM at T+7).
    Separates into clean observations and flagged outliers with full diagnostics.
    """
    if not observations:
        return [], []

    valid_fares = [obs["total_fare"] for obs in observations if obs.get("total_fare", 0) > 0]
    if len(valid_fares) < 4:
        # Insufficient stratum samples to compute reliable robust statistics
        for obs in observations:
            obs["z_score"] = 0.0
            obs["is_outlier"] = False
        return observations, []

    q1, q3, lower_iqr, upper_iqr = compute_iqr_bounds(valid_fares, multiplier=iqr_multiplier)
    med, mad = compute_mad_stats(valid_fares)

    clean_list = []
    outlier_list = []

    for obs in observations:
        fare = obs.get("total_fare", 0.0)
        z_score = compute_robust_z_score(fare, med, mad)
        obs["z_score"] = round(z_score, 3)

        is_iqr_outlier = (fare < lower_iqr or fare > upper_iqr)
        is_mad_outlier = abs(z_score) > mad_z_threshold

        # If flagged by either robust statistical method
        if is_iqr_outlier or is_mad_outlier:
            obs["is_outlier"] = True
            obs["outlier_diagnostic"] = {
                "iqr_bounds": [round(lower_iqr, 2), round(upper_iqr, 2)],
                "median": round(med, 2),
                "mad": round(mad, 2),
                "z_score": round(z_score, 3),
                "method_flags": {
                    "iqr_flagged": is_iqr_outlier,
                    "mad_flagged": is_mad_outlier
                }
            }
            outlier_list.append(obs)
        else:
            obs["is_outlier"] = False
            clean_list.append(obs)

    return clean_list, outlier_list
