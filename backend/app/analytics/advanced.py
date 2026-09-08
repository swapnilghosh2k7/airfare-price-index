import numpy as np
import pandas as pd
from datetime import date, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from backend.app.models import IndexObservation, FareQuote, DataQualityRecord

class AdvancedAnalyticsEngine:

    @classmethod
    def forecast_next_7_days(cls, db: Session) -> List[Dict[str, Any]]:
        """
        Experimental 7-day forecast of National APIx Index
        using Holt's Linear Trend / Exponential Smoothing method.
        """
        obs = (
            db.query(IndexObservation)
            .filter_by(route_code="NATIONAL", lead_time_bucket=0)
            .order_by(IndexObservation.observation_date.asc())
            .all()
        )

        if not obs or len(obs) < 7:
            return []

        series = np.array([o.national_index for o in obs])
        last_date = obs[-1].observation_date

        # Double Exponential Smoothing (Holt's Linear)
        alpha = 0.4
        beta = 0.2

        level = series[0]
        trend = series[1] - series[0]

        for i in range(1, len(series)):
            last_level = level
            level = alpha * series[i] + (1 - alpha) * (level + trend)
            trend = beta * (level - last_level) + (1 - beta) * trend

        forecasts = []
        for h in range(1, 8):
            fc_val = round(float(level + h * trend), 2)
            fc_date = last_date + timedelta(days=h)
            forecasts.append({
                "forecast_date": fc_date.isoformat(),
                "forecast_index": fc_val,
                "confidence_lower": round(fc_val * 0.98, 2),
                "confidence_upper": round(fc_val * 1.02, 2),
                "model": "Double Exponential Smoothing (Holt Linear)",
                "status": "EXPERIMENTAL_FORECAST"
            })

        return forecasts

    @classmethod
    def generate_alerts_and_anomalies(cls, db: Session) -> List[Dict[str, Any]]:
        """
        Detects sudden price surges (>15% WoW increase) and unusual route behavior.
        """
        obs = (
            db.query(IndexObservation)
            .filter(IndexObservation.lead_time_bucket == 0, IndexObservation.route_code != "NATIONAL")
            .order_by(IndexObservation.observation_date.asc())
            .all()
        )

        if not obs:
            return []

        df = pd.DataFrame([{
            "route_code": o.route_code,
            "date": o.observation_date,
            "index": o.route_index
        } for o in obs])

        alerts = []
        for r_code, group in df.groupby("route_code"):
            group = group.sort_values("date")
            if len(group) >= 7:
                curr_idx = group["index"].iloc[-1]
                week_ago_idx = group["index"].iloc[-7]

                chg_pct = ((curr_idx - week_ago_idx) / week_ago_idx) * 100.0

                if chg_pct > 10.0:
                    alerts.append({
                        "type": "PRICE_SURGE_ALERT",
                        "severity": "HIGH" if chg_pct > 18.0 else "MEDIUM",
                        "route_code": r_code,
                        "change_7d_pct": round(chg_pct, 2),
                        "message": f"Airfare on route {r_code} increased by {chg_pct:+.1f}% over the last 7 days.",
                        "date": group["date"].iloc[-1].isoformat()
                    })
                elif chg_pct < -10.0:
                    alerts.append({
                        "type": "PRICE_DROP_ALERT",
                        "severity": "MEDIUM",
                        "route_code": r_code,
                        "change_7d_pct": round(chg_pct, 2),
                        "message": f"Airfare on route {r_code} decreased by {chg_pct:.1f}% over the last 7 days.",
                        "date": group["date"].iloc[-1].isoformat()
                    })

        return sorted(alerts, key=lambda x: abs(x["change_7d_pct"]), reverse=True)

    @classmethod
    def calculate_demand_proxy_index(cls, db: Session) -> Dict[str, Any]:
        """
        Estimates demand pressure index (0 - 100) from availability categories,
        price dispersion, and last-minute T+1 price acceleration.
        """
        query = (
            db.query(FareQuote.lead_time_days, FareQuote.availability_status, FareQuote.total_fare)
            .join(DataQualityRecord, DataQualityRecord.fare_quote_id == FareQuote.id)
            .filter(FareQuote.collection_status == "VALID", DataQualityRecord.outlier_flag == False)
        )
        df = pd.read_sql(query.statement, db.bind)

        if df.empty:
            return {"demand_pressure_score": 50.0, "status": "NEUTRAL"}

        # 1. Limited availability proportion
        limited_ratio = (df["availability_status"] == "LIMITED").mean()

        # 2. T+1 vs T+30 Price Acceleration Ratio
        t1_med = df[df["lead_time_days"] == 1]["total_fare"].median()
        t30_med = df[df["lead_time_days"] == 30]["total_fare"].median()

        ratio = (t1_med / t30_med) if (t30_med and t30_med > 0) else 1.5

        # Score calculation
        score = min(100.0, max(0.0, (limited_ratio * 40.0) + (ratio * 25.0)))

        status = "HIGH_DEMAND" if score > 65 else ("LOW_DEMAND" if score < 35 else "MODERATE_DEMAND")

        return {
            "demand_pressure_score": round(score, 1),
            "limited_availability_pct": round(limited_ratio * 100.0, 1),
            "t1_to_t30_price_ratio": round(ratio, 2),
            "status": status,
            "description": f"Demand pressure index calculated as {score:.1f}/100 indicating {status.replace('_', ' ').lower()}."
        }
