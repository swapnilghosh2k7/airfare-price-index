import math
from fastapi import APIRouter, Depends, Query
from typing import Optional, List
from datetime import date
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import FareQuote
from backend.app.schemas.fare import FareQuoteSchema, PaginatedFareQuotes

router = APIRouter()

@router.get("/fares", response_model=PaginatedFareQuotes)
def search_fares(
    route: Optional[str] = Query(None, description="e.g. DEL-BOM"),
    carrier: Optional[str] = Query(None, description="e.g. IndiGo"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    lead_time: Optional[int] = Query(None),
    source: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(FareQuote)

    if route:
        if "-" in route:
            orig, dest = route.split("-")
            query = query.filter(FareQuote.origin == orig.upper(), FareQuote.destination == dest.upper())
        else:
            query = query.filter((FareQuote.origin == route.upper()) | (FareQuote.destination == route.upper()))

    if carrier:
        query = query.filter(FareQuote.carrier.ilike(f"%{carrier}%"))

    if start_date:
        query = query.filter(FareQuote.departure_date >= start_date)

    if end_date:
        query = query.filter(FareQuote.departure_date <= end_date)

    if lead_time is not None:
        query = query.filter(FareQuote.lead_time_days == lead_time)

    if source:
        query = query.filter(FareQuote.source == source)

    total = query.count()
    pages = math.ceil(total / size) if total > 0 else 1

    records = query.order_by(FareQuote.observation_timestamp.desc()).offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "data": records
    }

@router.get("/fares/latest", response_model=List[FareQuoteSchema])
def get_latest_fares(limit: int = Query(20, le=100), db: Session = Depends(get_db)):
    return db.query(FareQuote).order_by(FareQuote.observation_timestamp.desc()).limit(limit).all()
