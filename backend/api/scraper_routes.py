"""
Scraper Monitoring and Orchestration Endpoints
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database import get_db
from backend.models.db_models import Source, ScrapeRun, ScrapeError
from backend.scrapers.orchestrator import ScraperOrchestrator

router = APIRouter(prefix="/scraper", tags=["Scraper Orchestrator & Monitoring"])

@router.get("/status")
def get_scraper_status(db: Session = Depends(get_db)):
    """
    Returns real-time health and scraping metrics across all 11 adapters:
    5 Airlines + 6 OTAs with LIVE, MOCK, UNAVAILABLE, or ERROR status.
    """
    orchestrator = ScraperOrchestrator(db)
    sources = orchestrator.get_source_statuses()

    live_count = sum(1 for s in sources if s["status"] == "LIVE")
    mock_count = sum(1 for s in sources if s["status"] == "MOCK")
    error_count = sum(1 for s in sources if s["status"] in ("ERROR", "UNAVAILABLE"))
    total_collected = sum(s["records_collected"] for s in sources)
    total_rejected = sum(s["records_rejected"] for s in sources)

    last_run = db.query(ScrapeRun).order_by(ScrapeRun.started_at.desc()).first()

    return {
        "sources": sources,
        "total_sources": len(sources),
        "active_sources": sum(1 for s in sources if s["enabled"]),
        "live_count": live_count,
        "mock_count": mock_count,
        "error_count": error_count,
        "total_collected": total_collected,
        "total_rejected": total_rejected,
        "last_run_at": last_run.started_at if last_run else None,
        "last_run_status": last_run.status if last_run else "IDLE",
        "next_scheduled_run": (datetime.utcnow() + timedelta(hours=6)),
        "scheduler_active": True
    }

@router.post("/trigger")
def trigger_collection_now(
    background_tasks: BackgroundTasks,
    scoped: bool = False,
    db: Session = Depends(get_db)
):
    """
    Manual 'Run Collection Now' action button.
    Executes multi-source extraction, pipeline cleaning, and index recalculation.
    """
    orchestrator = ScraperOrchestrator(db)
    # If scoped=True, runs on top 5 routes for fast interactive UI feedback
    max_routes = 5 if scoped else None
    result = orchestrator.run_collection_cycle(trigger_type="MANUAL", max_routes=max_routes)
    return result

@router.get("/runs")
def get_scrape_runs(limit: int = 10, db: Session = Depends(get_db)):
    """Returns recent scraping audit execution runs"""
    runs = db.query(ScrapeRun).order_by(ScrapeRun.started_at.desc()).limit(limit).all()
    return [
        {
            "run_id": r.run_id,
            "trigger_type": r.trigger_type,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            "status": r.status,
            "sources_attempted": r.sources_attempted,
            "records_collected": r.records_collected,
            "records_cleaned": r.records_cleaned,
            "records_rejected": r.records_rejected,
            "error_count": r.error_count
        }
        for r in runs
    ]

@router.get("/errors")
def get_scrape_errors(limit: int = 15, db: Session = Depends(get_db)):
    """Returns recent scraper logs, CAPTCHA blocks, and rate-limiting events"""
    errs = db.query(ScrapeError).order_by(ScrapeError.timestamp.desc()).limit(limit).all()
    return [
        {
            "error_id": e.error_id,
            "source_name": e.source_name,
            "error_type": e.error_type,
            "status_code": e.status_code,
            "error_message": e.error_message,
            "timestamp": e.timestamp.isoformat()
        }
        for e in errs
    ]
