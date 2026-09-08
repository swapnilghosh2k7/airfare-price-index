import pandas as pd
import numpy as np
from fastapi import APIRouter, Depends, Query
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import FareQuote, DataQualityRecord, IndexObservation
from backend.app.analytics.advanced import AdvancedAnalyticsEngine

router = APIRouter()

@router.get("/analytics/lead-time")
def get_lead_time_analytics(
    route: Optional[str] = Query(None, description="e.g. DEL-BOM"),
    db: Session = Depends(get_db)
):
    """Calculates median total fare across advance purchase windows (T+1 to T+45)"""
    query = (
        db.query(
            FareQuote.origin,
            FareQuote.destination,
            FareQuote.lead_time_days,
            FareQuote.total_fare,
            FareQuote.base_fare,
            FareQuote.taxes
        )
        .join(DataQualityRecord, DataQualityRecord.fare_quote_id == FareQuote.id)
        .filter(
            FareQuote.collection_status == "VALID",
            DataQualityRecord.outlier_flag == False,
            FareQuote.total_fare > 0
        )
    )

    if route and "-" in route:
        orig, dest = route.split("-")
        query = query.filter(FareQuote.origin == orig.upper(), FareQuote.destination == dest.upper())

    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return []

    result = []
    for lead in [1, 7, 15, 30, 45]:
        sub = df[df["lead_time_days"] == lead]
        if not sub.empty:
            result.append({
                "lead_time_days": lead,
                "lead_time_label": f"T+{lead}",
                "median_fare": round(float(sub["total_fare"].median()), 2),
                "mean_fare": round(float(sub["total_fare"].mean()), 2),
                "min_fare": round(float(sub["total_fare"].min()), 2),
                "max_fare": round(float(sub["total_fare"].max()), 2),
                "sample_count": len(sub)
            })
    return result

@router.get("/analytics/carriers")
def get_carrier_analytics(
    route: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Carrier price comparison & fee composition breakdown"""
    query = (
        db.query(
            FareQuote.carrier,
            FareQuote.total_fare,
            FareQuote.base_fare,
            FareQuote.taxes,
            FareQuote.airport_fee,
            FareQuote.fuel_surcharge,
            FareQuote.convenience_fee,
            FareQuote.user_development_fee
        )
        .join(DataQualityRecord, DataQualityRecord.fare_quote_id == FareQuote.id)
        .filter(
            FareQuote.collection_status == "VALID",
            DataQualityRecord.outlier_flag == False,
            FareQuote.total_fare > 0
        )
    )

    if route and "-" in route:
        orig, dest = route.split("-")
        query = query.filter(FareQuote.origin == orig.upper(), FareQuote.destination == dest.upper())

    df = pd.read_sql(query.statement, db.bind)
    if df.empty:
        return []

    results = []
    for carrier_name, group in df.groupby("carrier"):
        results.append({
            "carrier": carrier_name,
            "median_total_fare": round(float(group["total_fare"].median()), 2),
            "mean_base_fare": round(float(group["base_fare"].mean()), 2),
            "mean_taxes": round(float(group["taxes"].mean()), 2),
            "mean_airport_fee": round(float(group["airport_fee"].mean()), 2),
            "mean_fuel_surcharge": round(float(group["fuel_surcharge"].mean()), 2),
            "mean_convenience_fee": round(float(group["convenience_fee"].mean()), 2),
            "mean_user_development_fee": round(float(group["user_development_fee"].mean()), 2),
            "quote_count": len(group)
        })

    return sorted(results, key=lambda x: x["median_total_fare"])

@router.get("/analytics/routes")
def get_route_analytics(db: Session = Depends(get_db)):
    """Route inflation, price volatility (std-dev & CV) metrics"""
    obs_query = (
        db.query(IndexObservation)
        .filter(IndexObservation.lead_time_bucket == 0, IndexObservation.route_code != "NATIONAL")
        .order_by(IndexObservation.observation_date.asc())
    )
    df_obs = pd.read_sql(obs_query.statement, db.bind)
    if df_obs.empty:
        return []

    results = []
    for r_code, group in df_obs.groupby("route_code"):
        group = group.sort_values("observation_date")
        indices = group["route_index"]
        
        earliest_idx = float(indices.iloc[0])
        latest_idx = float(indices.iloc[-1])
        
        cumulative_inflation = round(((latest_idx - earliest_idx) / earliest_idx) * 100.0, 2)
        
        std_dev = round(float(indices.std()), 2) if len(indices) > 1 else 0.0
        mean_val = float(indices.mean())
        cv_pct = round((std_dev / mean_val) * 100.0, 2) if mean_val > 0 else 0.0

        results.append({
            "route_code": r_code,
            "current_route_index": latest_idx,
            "earliest_route_index": earliest_idx,
            "inflation_30d_pct": cumulative_inflation,
            "volatility_std_dev": std_dev,
            "coefficient_of_variation_pct": cv_pct,
            "observation_days": len(group)
        })

    return sorted(results, key=lambda x: x["inflation_30d_pct"], reverse=True)

@router.get("/analytics/forecast")
def get_experimental_forecast(db: Session = Depends(get_db)):
    """Experimental 7-day Holt linear trend forecast of National APIx index"""
    return AdvancedAnalyticsEngine.forecast_next_7_days(db)

@router.get("/analytics/alerts")
def get_price_alerts(db: Session = Depends(get_db)):
    """Automated price surge and drop economic alerts"""
    return AdvancedAnalyticsEngine.generate_alerts_and_anomalies(db)

@router.get("/analytics/demand-proxy")
def get_demand_pressure_proxy(db: Session = Depends(get_db)):
    """Synthetic demand pressure index calculation"""
    return AdvancedAnalyticsEngine.calculate_demand_pressure_index(db)
