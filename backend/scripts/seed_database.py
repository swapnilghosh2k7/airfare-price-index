"""
Database Seeding Script for APIx Platform
Seeds initial routes, airlines, sources, 30-day realistic historical airfare dataset,
executes the cleaning pipeline, calculates historical daily APIx indices, and generates backtest results.
"""

import sys
import os
import uuid
from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from backend.database import SessionLocal, init_db
from backend.models.db_models import (
    Route, Airline, Source, FareObservationRaw, FareObservationClean,
    RejectedObservation, ScrapeRun, IndexValue
)
from backend.config import (
    INITIAL_ROUTES, INITIAL_AIRLINES, INITIAL_SOURCES,
    ADVANCE_PURCHASE_WINDOWS, BASE_PERIOD_DATE
)
from backend.synthetic.generator import generate_multi_day_dataset
from backend.pipeline.cleaner import DataCleaningPipeline
from backend.index.engine import APIxIndexEngine
from backend.backtest.engine import BacktestEngine

def seed_initial_platform_data(db: Session, force: bool = False):
    """Populates initial reference data and 30 days of clean observations"""
    # 1. Routes
    if force or db.query(Route).count() == 0:
        print("[SEED] Seeding 20 representative domestic routes...")
        for r_dict in INITIAL_ROUTES:
            route = Route(
                origin=r_dict["origin"],
                destination=r_dict["destination"],
                route_code=r_dict["route_code"],
                region=r_dict["region"],
                weight=r_dict["weight"],
                traffic_volume=r_dict["traffic_volume"],
                is_active=True
            )
            db.add(route)
        db.commit()

    # 2. Airlines
    if force or db.query(Airline).count() == 0:
        print("[SEED] Seeding 5 domestic airlines...")
        for a_dict in INITIAL_AIRLINES:
            airline = Airline(
                airline_name=a_dict["airline_name"],
                iata_code=a_dict["iata_code"],
                tier=a_dict["tier"],
                market_share=a_dict["market_share"],
                is_active=True
            )
            db.add(airline)
        db.commit()

    # 3. Sources
    if force or db.query(Source).count() == 0:
        print("[SEED] Seeding 11 scraping adapters (5 Airlines + 6 OTAs)...")
        for s_dict in INITIAL_SOURCES:
            source = Source(
                source_name=s_dict["source_name"],
                source_type=s_dict["source_type"],
                domain=s_dict["domain"],
                enabled=True,
                robots_allowed=True,
                rate_limit_rps=s_dict["rate_limit_rps"],
                status=s_dict["status"],
                last_scrape_at=datetime.utcnow(),
                records_collected=0,
                records_rejected=0
            )
            db.add(source)
        db.commit()

    # 4. Generate & Clean 30-Day Airfare Dataset
    clean_count = db.query(FareObservationClean).count()
    if force or clean_count < 1000:
        print("[SEED] Generating 30-day realistic domestic airfare dataset...")
        raw_dataset = generate_multi_day_dataset(
            days_back=30,
            quotes_per_window=1  # Ensures fast seeding with over 3,000 rich quotes
        )

        run_id = str(uuid.uuid4())
        scrape_run = ScrapeRun(
            run_id=run_id,
            trigger_type="SCHEDULED",
            started_at=datetime.utcnow() - timedelta(minutes=5),
            finished_at=datetime.utcnow(),
            status="COMPLETED",
            sources_attempted=11
        )
        db.add(scrape_run)
        db.commit()

        print(f"[SEED] Raw quotes generated: {len(raw_dataset)}. Running through 12-step cleaning pipeline...")
        cleaner = DataCleaningPipeline()
        clean_quotes, rejected_quotes = cleaner.clean_batch(raw_dataset)
        print(f"[SEED] Pipeline results: {len(clean_quotes)} clean quotes accepted, {len(rejected_quotes)} rejected.")

        # Batch insert raw
        raw_objs = []
        for q in raw_dataset:
            obs_id = str(uuid.uuid4())
            q["observation_id"] = obs_id
            raw_objs.append(
                FareObservationRaw(
                    observation_id=obs_id,
                    timestamp=datetime.utcnow(),
                    search_date=q["search_date"],
                    travel_date=q["travel_date"],
                    origin=q["origin"],
                    destination=q["destination"],
                    route=q["route"],
                    airline=q["airline"],
                    source=q["source"],
                    source_type=q["source_type"],
                    flight_number=q["flight_number"],
                    departure_time=q.get("departure_time"),
                    arrival_time=q.get("arrival_time"),
                    duration=q.get("duration"),
                    stops=q.get("stops", 0),
                    fare_class="Economy",
                    refundable=q.get("refundable", False),
                    base_fare=q["base_fare"],
                    taxes=q["taxes"],
                    airport_fee=q.get("airport_fee", 0.0),
                    user_development_fee=q.get("user_development_fee", 0.0),
                    convenience_fee=q.get("convenience_fee", 0.0),
                    fuel_surcharge=q.get("fuel_surcharge", 0.0),
                    total_fare=q["total_fare"],
                    currency="INR",
                    advance_purchase_days=q["advance_purchase_days"],
                    availability_status="AVAILABLE" if q["total_fare"] > 0 else "SOLD_OUT",
                    scrape_status="SUCCESS",
                    scrape_run_id=run_id
                )
            )
        db.bulk_save_objects(raw_objs)

        # Batch insert clean
        clean_objs = []
        for cq in clean_quotes:
            clean_objs.append(
                FareObservationClean(
                    clean_id=str(uuid.uuid4()),
                    raw_observation_id=cq.get("observation_id", str(uuid.uuid4())),
                    timestamp=datetime.utcnow(),
                    search_date=cq["search_date"],
                    travel_date=cq["travel_date"],
                    origin=cq["origin"],
                    destination=cq["destination"],
                    route=cq["route"],
                    airline=cq["airline"],
                    source=cq["source"],
                    source_type=cq["source_type"],
                    flight_number=cq["flight_number"],
                    departure_time=cq.get("departure_time"),
                    arrival_time=cq.get("arrival_time"),
                    duration=cq.get("duration"),
                    stops=cq.get("stops", 0),
                    fare_class="Economy",
                    base_fare=cq["base_fare"],
                    taxes=cq["taxes"],
                    airport_fee=cq.get("airport_fee", 0.0),
                    user_development_fee=cq.get("user_development_fee", 0.0),
                    convenience_fee=cq.get("convenience_fee", 0.0),
                    fuel_surcharge=cq.get("fuel_surcharge", 0.0),
                    total_fare=cq["total_fare"],
                    currency="INR",
                    advance_purchase_days=cq["advance_purchase_days"],
                    z_score=cq.get("z_score", 0.0),
                    is_outlier=cq.get("is_outlier", False),
                    cleaned_at=datetime.utcnow()
                )
            )
        db.bulk_save_objects(clean_objs)

        # Batch insert rejected
        rej_objs = []
        for rj in rejected_quotes:
            rq = rj["raw_quote"]
            rej_objs.append(
                RejectedObservation(
                    rejection_id=str(uuid.uuid4()),
                    raw_observation_id=rq.get("observation_id"),
                    timestamp=datetime.utcnow(),
                    search_date=rq.get("search_date"),
                    route=rq.get("route"),
                    airline=rq.get("airline"),
                    source=rq.get("source"),
                    base_fare=rq.get("base_fare"),
                    total_fare=rq.get("total_fare"),
                    rejection_reason=rj["rejection_reason"],
                    rejection_details=rj.get("rejection_details"),
                    rejected_at=datetime.utcnow()
                )
            )
        db.bulk_save_objects(rej_objs)

        scrape_run.records_collected = len(raw_dataset)
        scrape_run.records_cleaned = len(clean_quotes)
        scrape_run.records_rejected = len(rejected_quotes)
        db.commit()

        # Update sources records collected count
        for src in db.query(Source).all():
            src.records_collected = len(clean_quotes) // 11
            src.records_rejected = len(rejected_quotes) // 11
            src.requests_successful = 60
        db.commit()

        # 5. Calculate Historical APIx Indices
        print("[SEED] Calculating 30-day daily APIx indices...")
        today = date.today()
        base_dt = date.fromisoformat(BASE_PERIOD_DATE)
        index_engine = APIxIndexEngine(db)
        index_engine.compute_all_historical_indices(
            start_date=today - timedelta(days=30),
            end_date=today,
            base_date=base_dt
        )

        # 6. Run 30-Day Backtest vs DGCA Reference Series
        print("[SEED] Generating 30-day DGCA benchmark backtest comparison...")
        backtest_engine = BacktestEngine(db)
        backtest_engine.run_backtest(
            start_date=today - timedelta(days=30),
            end_date=today,
            is_synthetic=True
        )

        print("[SEED] Platform data seeding completed successfully.")

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    try:
        seed_initial_platform_data(db, force=True)
    finally:
        db.close()
