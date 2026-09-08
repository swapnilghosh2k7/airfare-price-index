from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import FareQuote, DataQualityRecord, DataCollectionRun
from backend.app.schemas.quality import DataQualitySummarySchema, CollectionRunSchema
from typing import List

router = APIRouter()

@router.get("/data-quality", response_model=DataQualitySummarySchema)
def get_data_quality_summary(db: Session = Depends(get_db)):
    total = db.query(FareQuote).count()
    outliers = db.query(DataQualityRecord).filter_by(outlier_flag=True).count()
    duplicates = db.query(DataQualityRecord).filter_by(duplicate_flag=True).count()
    
    records = db.query(DataQualityRecord).all()
    if records:
        mean_score = sum(r.quality_score for r in records) / len(records)
    else:
        mean_score = 100.0

    valid_count = total - (outliers + duplicates)

    return {
        "total_quotes": total,
        "valid_quotes": max(0, valid_count),
        "outlier_quotes": outliers,
        "duplicate_quotes": duplicates,
        "average_quality_score": round(mean_score, 2),
        "missing_fields_count": 0
    }

@router.get("/collection-runs", response_model=List[CollectionRunSchema])
def get_collection_runs(limit: int = 20, db: Session = Depends(get_db)):
    runs = db.query(DataCollectionRun).order_by(DataCollectionRun.started_at.desc()).limit(limit).all()
    res = []
    for r in runs:
        res.append({
            "id": r.id,
            "started_at": r.started_at.isoformat() if r.started_at else "",
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "source": r.source,
            "routes_requested": r.routes_requested,
            "quotes_collected": r.quotes_collected,
            "quotes_valid": r.quotes_valid,
            "quotes_rejected": r.quotes_rejected,
            "status": r.status,
            "error_summary": r.error_summary
        })
    return res
