"""
APIx Index Endpoints
"""

from datetime import date, datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.db_models import IndexValue, Route
from backend.analytics.service import AnalyticsService
from backend.config import BASE_PERIOD_DATE

router = APIRouter(prefix="/index", tags=["APIx Index"])

@router.get("/current")
def get_current_index(db: Session = Depends(get_db)):
    """Returns the most recent APIx calculation, 24h change, weekly, and monthly changes"""
    svc = AnalyticsService(db)
    return svc.get_kpi_summary()

@router.get("/daily")
def get_daily_index_series(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 90,
    db: Session = Depends(get_db)
):
    """Returns daily historical APIx time series"""
    query = (
        db.query(IndexValue)
        .filter(IndexValue.frequency == "DAILY")
        .order_by(IndexValue.index_date.asc())
    )

    if start_date:
        query = query.filter(IndexValue.index_date >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(IndexValue.index_date <= date.fromisoformat(end_date))

    records = query.limit(limit).all()

    points = []
    prev_apix = None
    for r in records:
        day_chg = round(((r.apix_value - prev_apix) / prev_apix) * 100.0, 2) if prev_apix else 0.0
        prev_apix = r.apix_value
        points.append({
            "date": r.index_date.isoformat(),
            "apix_value": r.apix_value,
            "average_fare": r.current_weighted_fare,
            "base_period_fare": r.base_period_fare,
            "price_relative": r.price_relative,
            "daily_change_pct": day_chg,
            "observation_count": r.observation_count
        })

    return {
        "frequency": "DAILY",
        "points": points,
        "base_period_date": BASE_PERIOD_DATE,
        "total_points": len(points)
    }

@router.get("/weekly")
def get_weekly_index_series(db: Session = Depends(get_db)):
    """Calculates weekly rolling average APIx values"""
    daily_pts = get_daily_index_series(limit=180, db=db)["points"]
    if not daily_pts:
        return {"frequency": "WEEKLY", "points": [], "total_points": 0}

    # Group into 7-day intervals
    weekly_pts = []
    chunk_size = 7
    for i in range(0, len(daily_pts), chunk_size):
        chunk = daily_pts[i:i + chunk_size]
        avg_apix = sum(p["apix_value"] for p in chunk) / len(chunk)
        avg_fare = sum(p["average_fare"] for p in chunk) / len(chunk)
        weekly_pts.append({
            "date": chunk[-1]["date"],
            "apix_value": round(avg_apix, 2),
            "average_fare": round(avg_fare, 2),
            "observation_count": sum(p["observation_count"] for p in chunk)
        })

    return {
        "frequency": "WEEKLY",
        "points": weekly_pts,
        "base_period_date": BASE_PERIOD_DATE,
        "total_points": len(weekly_pts)
    }

@router.get("/monthly")
def get_monthly_index_series(db: Session = Depends(get_db)):
    """Calculates monthly index values"""
    daily_pts = get_daily_index_series(limit=365, db=db)["points"]
    if not daily_pts:
        return {"frequency": "MONTHLY", "points": [], "total_points": 0}

    # Group into 30-day buckets
    monthly_pts = []
    chunk_size = 30
    for i in range(0, len(daily_pts), chunk_size):
        chunk = daily_pts[i:i + chunk_size]
        avg_apix = sum(p["apix_value"] for p in chunk) / len(chunk)
        avg_fare = sum(p["average_fare"] for p in chunk) / len(chunk)
        monthly_pts.append({
            "date": chunk[-1]["date"],
            "apix_value": round(avg_apix, 2),
            "average_fare": round(avg_fare, 2),
            "observation_count": sum(p["observation_count"] for p in chunk)
        })

    return {
        "frequency": "MONTHLY",
        "points": monthly_pts,
        "base_period_date": BASE_PERIOD_DATE,
        "total_points": len(monthly_pts)
    }

@router.get("/methodology")
def get_methodology_specs(db: Session = Depends(get_db)):
    """Returns transparent formula, weights, and base period parameters for auditability"""
    routes = db.query(Route).filter(Route.is_active == True).all()
    route_weights = [
        {
            "route_code": r.route_code,
            "origin": r.origin,
            "destination": r.destination,
            "region": r.region,
            "weight": r.weight,
            "weight_pct": round(r.weight * 100.0, 2),
            "traffic_volume": r.traffic_volume
        }
        for r in routes
    ]

    return {
        "index_name": "APIx (Airfare Price Index)",
        "index_type": "Laspeyres-Type High-Frequency Weighted Price Relative",
        "base_period_date": BASE_PERIOD_DATE,
        "base_index_value": 100.0,
        "formula": "APIx_t = SUM( W_r * ( P_{r, t} / P_{r, t0} ) * 100 )",
        "route_basket_count": len(routes),
        "total_weight": round(sum(r["weight"] for r in route_weights), 4),
        "routes": route_weights,
        "advance_windows": ["T+1", "T+7", "T+15", "T+30", "T+45"],
        "data_sources_tracked": 11,
        "legal_notice": "Experimental research index designed for CPI Transport Subgroup augmentation under MoSPI/RBI guidelines."
    }
