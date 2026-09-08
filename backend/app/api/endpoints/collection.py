import sys
from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import DataCollectionRun
from datetime import datetime

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

router = APIRouter()

def execute_demo_pipeline():
    from scripts.generate_demo_data import generate_synthetic_quotes
    from scripts.load_demo_data import load_and_process_csv
    from scripts.build_index import run_index_build

    # 1. Generate quotes
    csv_file = PROJECT_ROOT / "data" / "sample" / "fare_quotes.csv"
    generate_synthetic_quotes(days=30, seed=42, output_path=str(csv_file))

    # 2. Load & Clean
    load_and_process_csv(str(csv_file))

    # 3. Build Index
    run_index_build()

@router.post("/collection/run-demo")
def trigger_demo_collection(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    run_rec = DataCollectionRun(
        started_at=datetime.utcnow(),
        source="mock_provider",
        routes_requested=10,
        quotes_collected=11460,
        quotes_valid=11000,
        quotes_rejected=460,
        status="COMPLETED",
        completed_at=datetime.utcnow()
    )
    db.add(run_rec)
    db.commit()

    background_tasks.add_task(execute_demo_pipeline)
    return {
        "status": "triggered",
        "message": "Demo data pipeline execution scheduled in background.",
        "run_id": run_rec.id
    }

@router.post("/collection/rebuild-index")
def trigger_rebuild_index(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    from scripts.build_index import run_index_build
    background_tasks.add_task(run_index_build)
    return {
        "status": "triggered",
        "message": "Airfare Price Index rebuild scheduled."
    }
