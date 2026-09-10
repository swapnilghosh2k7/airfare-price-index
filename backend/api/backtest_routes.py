"""
Backtesting and DGCA Benchmark Validation Endpoints
"""

import csv
import io
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Response
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.backtest.engine import BacktestEngine
from backend.models.db_models import BacktestResult

router = APIRouter(prefix="/backtest", tags=["Backtesting Engine"])

@router.get("")
def run_backtest_analysis(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Executes 30-day backtest comparing APIx against DGCA regulatory benchmark tariffs.
    Returns MAE, MAPE, RMSE, Pearson Correlation, and error distribution series.
    """
    engine = BacktestEngine(db)
    s_date = date.fromisoformat(start_date) if start_date else None
    e_date = date.fromisoformat(end_date) if end_date else None
    return engine.run_backtest(start_date=s_date, end_date=e_date, is_synthetic=True)

@router.post("/upload-dgca")
async def upload_dgca_reference_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Allows statistical analysts to upload real DGCA reference CSV data.
    Expected CSV columns: 'date' (YYYY-MM-DD), 'dgca_index' (or 'fare').
    """
    contents = await file.read()
    csv_text = contents.decode("utf-8", errors="ignore")

    engine = BacktestEngine(db)
    custom_reference = engine.parse_uploaded_csv(csv_text)

    if not custom_reference:
        return {"error": "Could not parse valid date and dgca_index columns from uploaded CSV file."}

    dates = sorted(custom_reference.keys())
    return engine.run_backtest(
        start_date=dates[0],
        end_date=dates[-1],
        external_reference=custom_reference,
        is_synthetic=False
    )

@router.get("/export")
def export_backtest_csv(db: Session = Depends(get_db)):
    """Exports backtest results with calculated errors and DGCA benchmark to CSV"""
    records = db.query(BacktestResult).order_by(BacktestResult.target_date.asc()).all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "target_date", "apix_value", "dgca_benchmark_index", "absolute_error",
        "percentage_error", "is_benchmark_synthetic"
    ])

    for r in records:
        writer.writerow([
            r.target_date.isoformat(), r.apix_value, r.dgca_benchmark_index,
            r.absolute_error, r.percentage_error, r.is_benchmark_synthetic
        ])

    response = Response(content=output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=apix_dgca_backtest.csv"
    return response
