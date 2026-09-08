import sys
import json
import argparse
import yaml
from pathlib import Path
from datetime import datetime, date
import pandas as pd
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.database.session import init_db, SessionLocal
from backend.app.models import Route, Carrier, FareQuote, DataQualityRecord
from backend.app.cleaning.normalizer import Normalizer
from backend.app.cleaning.deduplication import Deduplicator
from backend.app.cleaning.outliers import OutlierDetector
from backend.app.cleaning.quality_score import QualityScorer

def seed_routes_and_carriers(db: Session):
    # 1. Seed Routes from config/routes.yaml
    routes_file = PROJECT_ROOT / "config" / "routes.yaml"
    if routes_file.exists():
        with open(routes_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            routes_list = data.get("routes", [])
            for r in routes_list:
                existing = db.query(Route).filter_by(route_code=r["route_code"]).first()
                if not existing:
                    route_obj = Route(
                        route_code=r["route_code"],
                        origin=r["origin"],
                        destination=r["destination"],
                        origin_city=r["origin_city"],
                        destination_city=r["destination_city"],
                        weight=r["weight"],
                        active=r.get("active", True)
                    )
                    db.add(route_obj)
        db.commit()
        print("[AirFareX Loader] Seeded/Verified domestic routes from routes.yaml")

    # 2. Seed Default Carriers
    default_carriers = [
        {"name": "IndiGo", "iata_code": "6E", "source_type": "LCC"},
        {"name": "Air India", "iata_code": "AI", "source_type": "FSC"},
        {"name": "Vistara", "iata_code": "UK", "source_type": "FSC"},
        {"name": "Akasa Air", "iata_code": "QP", "source_type": "LCC"},
        {"name": "SpiceJet", "iata_code": "SG", "source_type": "LCC"},
    ]
    for c in default_carriers:
        existing = db.query(Carrier).filter_by(iata_code=c["iata_code"]).first()
        if not existing:
            db.add(Carrier(**c))
    db.commit()
    print("[AirFareX Loader] Seeded/Verified carrier master records.")

def load_and_process_csv(csv_path: str):
    init_db()
    db = SessionLocal()
    try:
        seed_routes_and_carriers(db)

        path = Path(csv_path)
        if not path.exists():
            print(f"[AirFareX Loader Error] Sample file not found at: {path}")
            return

        print(f"[AirFareX Loader] Reading raw CSV from {path}...")
        df = pd.read_csv(path)
        print(f"[AirFareX Loader] Raw quotes loaded: {len(df)}")

        # Step 1: Normalization
        raw_dicts = df.to_dict(orient="records")
        normalized_dicts = [Normalizer.process_quote_dict(q) for q in raw_dicts]

        # Step 2: Deduplication
        deduped_dicts = Deduplicator.flag_duplicates(normalized_dicts)

        # Step 3: Outlier Detection
        df_cleaned = pd.DataFrame(deduped_dicts)
        df_cleaned = OutlierDetector.flag_outliers(df_cleaned, method="MAD", mad_threshold=3.0)

        cleaned_dicts = df_cleaned.to_dict(orient="records")

        # Clear previous data for clean reload
        db.query(DataQualityRecord).delete()
        db.query(FareQuote).delete()
        db.commit()

        print("[AirFareX Loader] Inserting quotes & quality records into database...")

        fare_objects = []
        quality_objects = []

        for idx, item in enumerate(cleaned_dicts):
            # Parse dates
            obs_dt = datetime.fromisoformat(item["observation_timestamp"]) if isinstance(item["observation_timestamp"], str) else item["observation_timestamp"]
            dep_d = date.fromisoformat(item["departure_date"]) if isinstance(item["departure_date"], str) else item["departure_date"]

            fare = FareQuote(
                observation_timestamp=obs_dt,
                origin=item["origin"],
                destination=item["destination"],
                departure_date=dep_d,
                lead_time_days=int(item["lead_time_days"]),
                carrier=item["carrier"],
                flight_number=str(item["flight_number"]),
                fare_class=str(item.get("fare_class", "Economy")),
                base_fare=float(item.get("base_fare", 0.0)),
                taxes=float(item.get("taxes", 0.0)),
                airport_fee=float(item.get("airport_fee", 0.0)),
                fuel_surcharge=float(item.get("fuel_surcharge", 0.0)),
                user_development_fee=float(item.get("user_development_fee", 0.0)),
                convenience_fee=float(item.get("convenience_fee", 0.0)),
                other_fee=float(item.get("other_fee", 0.0)),
                total_fare=float(item["total_fare"]),
                currency=item.get("currency", "INR"),
                source=item.get("source", "mock_provider"),
                source_url=item.get("source_url"),
                availability_status=item.get("availability_status", "AVAILABLE"),
                collection_status=item.get("collection_status", "VALID"),
                raw_hash=item["raw_hash"]
            )
            db.add(fare)
            db.flush()  # assign fare.id

            # Evaluate Data Quality score
            score, missing, errors = QualityScorer.evaluate_quote(item)
            quality_rec = DataQualityRecord(
                fare_quote_id=fare.id,
                quality_score=score,
                missing_fields=json.dumps(missing),
                outlier_flag=bool(item.get("outlier_flag", False)),
                duplicate_flag=bool(item.get("duplicate_flag", False)),
                validation_errors=json.dumps(errors)
            )
            quality_objects.append(quality_rec)

        db.bulk_save_objects(quality_objects)
        db.commit()

        total_saved = db.query(FareQuote).count()
        outliers_count = db.query(DataQualityRecord).filter_by(outlier_flag=True).count()
        duplicates_count = db.query(DataQualityRecord).filter_by(duplicate_flag=True).count()
        avg_quality = db.query(DataQualityRecord).all()
        mean_score = sum(q.quality_score for q in avg_quality) / len(avg_quality) if avg_quality else 0.0

        print(f"[AirFareX Loader Success] Loaded {total_saved} fare quotes into SQLite database.")
        print(f"[AirFareX Quality Stats] Outliers Flagged: {outliers_count} | Duplicates Flagged: {duplicates_count} | Mean Quality Score: {mean_score:.2f}%")

    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load and clean sample fare quotes into AirFareX database")
    parser.add_argument("--csv", type=str, default="data/sample/fare_quotes.csv", help="Path to raw fare quotes CSV")
    args = parser.parse_args()
    
    csv_file = PROJECT_ROOT / args.csv
    load_and_process_csv(str(csv_file))
