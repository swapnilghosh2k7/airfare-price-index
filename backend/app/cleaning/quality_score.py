import json
from typing import Dict, Any, List, Tuple

class QualityScorer:
    MANDATORY_FIELDS = ["origin", "destination", "departure_date", "carrier", "total_fare"]

    @classmethod
    def evaluate_quote(cls, quote: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """
        Evaluates a single quote dict.
        Returns (quality_score, missing_fields, validation_errors)
        """
        score = 100.0
        missing = []
        errors = []

        # 1. Check mandatory fields
        for field in cls.MANDATORY_FIELDS:
            val = quote.get(field)
            if val is None or val == "" or (isinstance(val, (int, float)) and val <= 0):
                missing.append(field)
                score -= 15.0

        # 2. Check total fare component consistency
        reported_total = float(quote.get("total_fare", 0.0) or 0.0)
        reconstructed_total = float(quote.get("reconstructed_total", 0.0) or 0.0)
        
        if reported_total > 0 and reconstructed_total > 0:
            diff_pct = abs(reported_total - reconstructed_total) / reported_total
            if diff_pct > 0.05:
                errors.append(f"Component sum discrepancy ({diff_pct*100:.1f}%)")
                score -= 10.0

        # 3. Check duplicate flag
        if quote.get("duplicate_flag"):
            errors.append("Duplicate quote detected")
            score -= 25.0

        # 4. Check outlier flag
        if quote.get("outlier_flag"):
            errors.append("Statistical price outlier detected")
            score -= 15.0

        # 5. Check collection status
        if quote.get("collection_status") == "INVALID":
            errors.append("Invalid collection status")
            score -= 20.0

        final_score = max(0.0, min(100.0, score))
        return round(final_score, 2), missing, errors
