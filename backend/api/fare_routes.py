"""
Fare Observations Query and Export Endpoints
"""

import csv
import io
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.db_models import FareObservationClean, FareObservationRaw

router = APIRouter(prefix="/fares", tags=["Fare Observations"])

@router.get("")
def list_clean_fares(
    route: Optional[str] = None,
    airline: Optional[str] = None,
    source: Optional[str] = None,
    advance_purchase_days: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = Query(50, le=500),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Retrieves paginated, filtered clean airfare quotes"""
    query = db.query(FareObservationClean)

    if route:
        query = query.filter(FareObservationClean.route == route.upper())
    if airline:
        query = query.filter(FareObservationClean.airline == airline)
    if source:
        query = query.filter(FareObservationClean.source == source)
    if advance_purchase_days is not None:
        query = query.filter(FareObservationClean.advance_purchase_days == advance_purchase_days)
    if start_date:
        query = query.filter(FareObservationClean.search_date >= date.fromisoformat(start_date))
    if end_date:
        query = query.filter(FareObservationClean.search_date <= date.fromisoformat(end_date))

    total = query.count()
    records = query.order_by(FareObservationClean.search_date.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "fares": [
            {
                "observation_id": r.clean_id,
                "timestamp": r.timestamp.isoformat(),
                "search_date": r.search_date.isoformat(),
                "travel_date": r.travel_date.isoformat(),
                "origin": r.origin,
                "destination": r.destination,
                "route": r.route,
                "airline": r.airline,
                "source": r.source,
                "flight_number": r.flight_number,
                "departure_time": r.departure_time,
                "arrival_time": r.arrival_time,
                "duration": r.duration,
                "base_fare": r.base_fare,
                "taxes": r.taxes,
                "user_development_fee": r.user_development_fee,
                "fuel_surcharge": r.fuel_surcharge,
                "convenience_fee": r.convenience_fee,
                "total_fare": r.total_fare,
                "currency": r.currency,
                "advance_purchase_days": r.advance_purchase_days,
                "z_score": r.z_score,
                "is_outlier": r.is_outlier
            }
            for r in records
        ]
    }

@router.get("/latest")
def get_latest_fares(limit: int = 15, db: Session = Depends(get_db)):
    """Returns the most recent airfare observations captured by the system"""
    return list_clean_fares(limit=limit, offset=0, db=db)

@router.get("/export")
def export_fares_csv(
    route: Optional[str] = None,
    airline: Optional[str] = None,
    limit: int = 2000,
    db: Session = Depends(get_db)
):
    """Exports clean fare observations to CSV for statistical systems (NSO / RBI)"""
    query = db.query(FareObservationClean)
    if route:
        query = query.filter(FareObservationClean.route == route.upper())
    if airline:
        query = query.filter(FareObservationClean.airline == airline)

    records = query.order_by(FareObservationClean.search_date.desc()).limit(limit).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "observation_id", "search_date", "travel_date", "route", "origin", "destination",
        "airline", "source", "flight_number", "advance_days", "base_fare", "fuel_surcharge",
        "taxes", "udf", "convenience_fee", "total_fare", "currency", "z_score"
    ])

    for r in records:
        writer.writerow([
            r.clean_id, r.search_date.isoformat(), r.travel_date.isoformat(), r.route,
            r.origin, r.destination, r.airline, r.source, r.flight_number,
            r.advance_purchase_days, r.base_fare, r.fuel_surcharge, r.taxes,
            r.user_development_fee, r.convenience_fee, r.total_fare, r.currency, r.z_score
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=apix_clean_fares.csv"
    return response
