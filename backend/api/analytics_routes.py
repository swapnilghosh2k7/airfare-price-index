"""
Analytics and Visualization Endpoints
"""

from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics & Visualizations"])

@router.get("/kpis")
def get_kpi_cards(db: Session = Depends(get_db)):
    """Returns top KPI metrics (Current APIx, daily change, weekly, monthly, observations)"""
    svc = AnalyticsService(db)
    return svc.get_kpi_summary()

@router.get("/heatmap")
def get_route_heatmap(db: Session = Depends(get_db)):
    """Returns India domestic route heatmap metrics with contributions and volatility"""
    svc = AnalyticsService(db)
    return svc.get_route_heatmap_matrix()

@router.get("/lead-time")
def get_lead_time_curve(route: Optional[str] = None, db: Session = Depends(get_db)):
    """Returns lead-time elasticity curve across T+1, T+7, T+15, T+30, T+45"""
    svc = AnalyticsService(db)
    return svc.get_lead_time_elasticity(route_code=route.upper() if route else None)

@router.get("/route/{route_code}")
def get_route_analytics(route_code: str, db: Session = Depends(get_db)):
    """Deep-dive analytics for a specific domestic city-pair (e.g. DEL-BOM)"""
    svc = AnalyticsService(db)
    return svc.get_route_details(route_code.upper())

@router.get("/airlines")
def get_airline_comparison(db: Session = Depends(get_db)):
    """Comparative price and cost breakdown across Indian carriers"""
    svc = AnalyticsService(db)
    return svc.get_airline_market_comparison()

@router.get("/components")
def get_fare_components(db: Session = Depends(get_db)):
    """National average airfare component breakdown (Base vs Taxes vs Fuel vs UDF)"""
    svc = AnalyticsService(db)
    return svc.get_fare_component_breakdown()
