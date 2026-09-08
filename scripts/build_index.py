import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import SessionLocal, init_db
from backend.app.indexing.laspeyres import LaspeyresIndexCalculator
from backend.app.models import IndexObservation, FareQuote

def run_index_build():
    init_db()
    db = SessionLocal()
    try:
        quote_count = db.query(FareQuote).count()
        if quote_count == 0:
            print("[AirFareX Index Build Error] No fare quotes found in database. Run load_demo_data.py first.")
            return

        print(f"[AirFareX Index Build] Found {quote_count} fare quotes. Building Laspeyres Airfare Price Index (APIX_v1)...")
        obs_list = LaspeyresIndexCalculator.build_full_index_series(db)
        
        national_obs = db.query(IndexObservation).filter_by(route_code="NATIONAL", lead_time_bucket=0).order_by(IndexObservation.observation_date.desc()).all()
        
        if national_obs:
            latest = national_obs[0]
            earliest = national_obs[-1]
            print(f"[AirFareX Index Build Success] Generated {len(obs_list)} index observations.")
            print(f"[AirFareX Index Summary] Earliest Index ({earliest.observation_date}): {earliest.national_index:.2f}")
            print(f"[AirFareX Index Summary] Latest APIx Index ({latest.observation_date}): {latest.national_index:.2f}")
            
            chg = ((latest.national_index - earliest.national_index) / earliest.national_index) * 100.0
            print(f"[AirFareX Index Summary] 30-Day Cumulative APIx Change: {chg:+.2f}%")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Airfare Price Index (APIX_v1)")
    args = parser.parse_args()
    run_index_build()
