from fastapi import APIRouter, Depends, Query, HTTPException
from typing import Optional, List
from datetime import date, timedelta
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import IndexObservation, FareQuote
from backend.app.schemas.index import IndexObservationSchema, IndexSummaryResponse

router = APIRouter()

@router.get("/index", response_model=IndexSummaryResponse)
def get_index_summary(db: Session = Depends(get_db)):
    national_obs = (
        db.query(IndexObservation)
        .filter_by(route_code="NATIONAL", lead_time_bucket=0)
        .order_by(IndexObservation.observation_date.desc())
        .all()
    )

    if not national_obs:
        return {
            "latest_date": date.today(),
            "national_apix": 100.0,
            "daily_change_pct": 0.0,
            "weekly_change_pct": 0.0,
            "monthly_change_pct": 0.0,
            "total_observations": 0,
            "base_period": "2026-08-BASE30",
            "methodology_version": "APIX_v1"
        }

    latest = national_obs[0]
    total_quotes = db.query(FareQuote).count()

    # Calculate Daily, Weekly, Monthly changes
    latest_val = latest.national_index

    # 1D change
    val_1d = national_obs[1].national_index if len(national_obs) > 1 else latest_val
    daily_chg = round(((latest_val - val_1d) / val_1d) * 100.0, 2) if val_1d > 0 else 0.0

    # 7D change
    val_7d = national_obs[min(7, len(national_obs) - 1)].national_index if len(national_obs) > 1 else latest_val
    weekly_chg = round(((latest_val - val_7d) / val_7d) * 100.0, 2) if val_7d > 0 else 0.0

    # 30D change (or earliest in dataset)
    val_30d = national_obs[-1].national_index
    monthly_chg = round(((latest_val - val_30d) / val_30d) * 100.0, 2) if val_30d > 0 else 0.0

    return {
        "latest_date": latest.observation_date,
        "national_apix": latest.national_index,
        "daily_change_pct": daily_chg,
        "weekly_change_pct": weekly_chg,
        "monthly_change_pct": monthly_chg,
        "total_observations": total_quotes,
        "base_period": latest.base_period,
        "methodology_version": latest.methodology_version
    }

@router.get("/index/latest", response_model=List[IndexObservationSchema])
def get_latest_index(db: Session = Depends(get_db)):
    latest_date_sub = db.query(IndexObservation.observation_date).order_by(IndexObservation.observation_date.desc()).first()
    if not latest_date_sub:
        return []
    target_d = latest_date_sub[0]
    return db.query(IndexObservation).filter_by(observation_date=target_d, lead_time_bucket=0).all()

@router.get("/index/history", response_model=List[IndexObservationSchema])
def get_index_history(
    route: Optional[str] = Query(None, description="e.g. NATIONAL or DEL-BOM"),
    lead_time: int = Query(0, description="0 for Composite ALL, or 1,7,15,30,45"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(IndexObservation).filter(IndexObservation.lead_time_bucket == lead_time)

    if route:
        query = query.filter(IndexObservation.route_code == route.upper())

    if start_date:
        query = query.filter(IndexObservation.observation_date >= start_date)

    if end_date:
        query = query.filter(IndexObservation.observation_date <= end_date)

    return query.order_by(IndexObservation.observation_date.asc()).all()

@router.get("/index/route/{route_code}", response_model=List[IndexObservationSchema])
def get_route_index_history(
    route_code: str,
    lead_time: int = Query(0),
    db: Session = Depends(get_db)
):
    obs = (
        db.query(IndexObservation)
        .filter(
            IndexObservation.route_code == route_code.upper(),
            IndexObservation.lead_time_bucket == lead_time
        )
        .order_by(IndexObservation.observation_date.asc())
        .all()
    )
    if not obs:
        raise HTTPException(status_code=404, detail=f"No index records found for route {route_code}")
    return obs
