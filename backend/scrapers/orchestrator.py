"""
Scraper Orchestrator
Coordinates multi-source data collection, database persistence, pipeline invocation, and index recalculation.
"""

import uuid
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.models.db_models import (
    Source, Route, FareObservationRaw, FareObservationClean,
    RejectedObservation, ScrapeRun, ScrapeError
)
from backend.scrapers.airline_adapters import (
    IndiGoAdapter, AirIndiaAdapter, AirIndiaExpressAdapter, AkasaAirAdapter, SpiceJetAdapter
)
from backend.scrapers.ota_adapters import (
    MakeMyTripAdapter, YatraAdapter, EaseMyTripAdapter, CleartripAdapter, IxigoAdapter, GoibiboAdapter
)
from backend.pipeline.cleaner import DataCleaningPipeline
from backend.index.engine import APIxIndexEngine
from backend.config import ADVANCE_PURCHASE_WINDOWS, BASE_PERIOD_DATE

class ScraperOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.adapters = {
            "IndiGo Portal": IndiGoAdapter(status="LIVE"),
            "Air India Portal": AirIndiaAdapter(status="MOCK"),
            "Air India Express Portal": AirIndiaExpressAdapter(status="MOCK"),
            "Akasa Air Portal": AkasaAirAdapter(status="MOCK"),
            "SpiceJet Portal": SpiceJetAdapter(status="MOCK"),
            "MakeMyTrip": MakeMyTripAdapter(),
            "Yatra": YatraAdapter(),
            "EaseMyTrip": EaseMyTripAdapter(),
            "Cleartrip": CleartripAdapter(),
            "Ixigo": IxigoAdapter(),
            "Goibibo": GoibiboAdapter(),
        }
        self.cleaner = DataCleaningPipeline()

    def get_source_statuses(self) -> List[Dict[str, Any]]:
        """Returns live status of all 11 adapters for the dashboard monitor"""
        result = []
        for name, adapter in self.adapters.items():
            # Query db for persisted metrics if available
            db_source = self.db.query(Source).filter(Source.source_name == name).first()
            if db_source:
                result.append({
                    "source_id": db_source.source_id,
                    "source_name": db_source.source_name,
                    "source_type": db_source.source_type,
                    "domain": db_source.domain,
                    "enabled": db_source.enabled,
                    "robots_allowed": db_source.robots_allowed,
                    "rate_limit_rps": db_source.rate_limit_rps,
                    "status": db_source.status,
                    "last_scrape_at": db_source.last_scrape_at,
                    "captcha_detected_count": db_source.captcha_detected_count,
                    "requests_successful": db_source.requests_successful,
                    "requests_failed": db_source.requests_failed,
                    "records_collected": db_source.records_collected,
                    "records_rejected": db_source.records_rejected,
                })
            else:
                result.append({
                    "source_id": 0,
                    "source_name": adapter.source_name,
                    "source_type": adapter.source_type,
                    "domain": adapter.domain,
                    "enabled": adapter.enabled,
                    "robots_allowed": adapter.robots_allowed,
                    "rate_limit_rps": adapter.rate_limit_rps,
                    "status": adapter.status,
                    "last_scrape_at": adapter.last_scrape_at,
                    "captcha_detected_count": adapter.captcha_detected_count,
                    "requests_successful": adapter.requests_successful,
                    "requests_failed": adapter.requests_failed,
                    "records_collected": adapter.records_collected,
                    "records_rejected": adapter.records_rejected,
                })
        return result

    def run_collection_cycle(
        self,
        trigger_type: str = "MANUAL",
        target_date: Optional[date] = None,
        max_routes: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Executes a full or scoped data collection cycle across active routes and sources.
        """
        search_date = target_date or date.today()
        run_id = str(uuid.uuid4())
        scrape_run = ScrapeRun(
            run_id=run_id,
            trigger_type=trigger_type,
            started_at=datetime.utcnow(),
            status="RUNNING"
        )
        self.db.add(scrape_run)
        self.db.commit()

        # Get active routes
        routes_query = self.db.query(Route).filter(Route.is_active == True)
        if max_routes:
            routes_query = routes_query.limit(max_routes)
        routes = routes_query.all()

        route_dicts = [
            {"origin": r.origin, "destination": r.destination, "route_code": r.route_code}
            for r in routes
        ]

        raw_observations = []
        sources_attempted = 0
        error_count = 0

        # Collect from each adapter
        for name, adapter in self.adapters.items():
            if not adapter.enabled:
                continue

            sources_attempted += 1
            source_raw = []

            # Check if blocked or disabled in db
            db_source = self.db.query(Source).filter(Source.source_name == name).first()
            if db_source and not db_source.enabled:
                continue

            try:
                for r_info in route_dicts:
                    for win in ADVANCE_PURCHASE_WINDOWS:
                        quotes = adapter.fetch_fares(
                            route_info=r_info,
                            search_date=search_date,
                            advance_days=win
                        )
                        for q in quotes:
                            q["scrape_run_id"] = run_id
                            source_raw.append(q)

                raw_observations.extend(source_raw)

                # Update source stats in DB
                if db_source:
                    db_source.requests_successful += adapter.requests_successful
                    db_source.records_collected += len(source_raw)
                    db_source.last_scrape_at = datetime.utcnow()
                    db_source.status = adapter.status
                    db_source.captcha_detected_count = adapter.captcha_detected_count

            except Exception as ex:
                error_count += 1
                scrape_err = ScrapeError(
                    run_id=run_id,
                    source_name=name,
                    error_type="COLLECTION_ERROR",
                    error_message=str(ex)
                )
                self.db.add(scrape_err)
                if db_source:
                    db_source.requests_failed += 1
                    db_source.status = "ERROR"

        # 1. Persist Raw Quotes
        raw_db_objects = []
        for r_quote in raw_observations:
            obs_id = str(uuid.uuid4())
            r_quote["observation_id"] = obs_id
            raw_obj = FareObservationRaw(
                observation_id=obs_id,
                timestamp=datetime.utcnow(),
                search_date=r_quote["search_date"],
                travel_date=r_quote["travel_date"],
                origin=r_quote["origin"],
                destination=r_quote["destination"],
                route=r_quote["route"],
                airline=r_quote["airline"],
                source=r_quote["source"],
                source_type=r_quote["source_type"],
                flight_number=r_quote["flight_number"],
                departure_time=r_quote.get("departure_time"),
                arrival_time=r_quote.get("arrival_time"),
                duration=r_quote.get("duration"),
                stops=r_quote.get("stops", 0),
                fare_class=r_quote.get("fare_class", "Economy"),
                refundable=r_quote.get("refundable", False),
                base_fare=r_quote["base_fare"],
                taxes=r_quote["taxes"],
                airport_fee=r_quote.get("airport_fee", 0.0),
                user_development_fee=r_quote.get("user_development_fee", 0.0),
                convenience_fee=r_quote.get("convenience_fee", 0.0),
                fuel_surcharge=r_quote.get("fuel_surcharge", 0.0),
                total_fare=r_quote["total_fare"],
                currency=r_quote.get("currency", "INR"),
                advance_purchase_days=r_quote["advance_purchase_days"],
                availability_status=r_quote.get("availability_status", "AVAILABLE"),
                scrape_status="SUCCESS",
                scrape_run_id=run_id
            )
            raw_db_objects.append(raw_obj)

        self.db.bulk_save_objects(raw_db_objects)
        self.db.commit()

        # 2. Run Data Cleaning Pipeline
        clean_quotes, rejected_quotes = self.cleaner.clean_batch(raw_observations)

        # 3. Persist Clean Quotes
        clean_db_objects = []
        for c_quote in clean_quotes:
            clean_obj = FareObservationClean(
                clean_id=str(uuid.uuid4()),
                raw_observation_id=c_quote.get("observation_id", str(uuid.uuid4())),
                timestamp=datetime.utcnow(),
                search_date=c_quote["search_date"],
                travel_date=c_quote["travel_date"],
                origin=c_quote["origin"],
                destination=c_quote["destination"],
                route=c_quote["route"],
                airline=c_quote["airline"],
                source=c_quote["source"],
                source_type=c_quote["source_type"],
                flight_number=c_quote["flight_number"],
                departure_time=c_quote.get("departure_time"),
                arrival_time=c_quote.get("arrival_time"),
                duration=c_quote.get("duration"),
                stops=c_quote.get("stops", 0),
                fare_class=c_quote.get("fare_class", "Economy"),
                base_fare=c_quote["base_fare"],
                taxes=c_quote["taxes"],
                airport_fee=c_quote.get("airport_fee", 0.0),
                user_development_fee=c_quote.get("user_development_fee", 0.0),
                convenience_fee=c_quote.get("convenience_fee", 0.0),
                fuel_surcharge=c_quote.get("fuel_surcharge", 0.0),
                total_fare=c_quote["total_fare"],
                currency=c_quote.get("currency", "INR"),
                advance_purchase_days=c_quote["advance_purchase_days"],
                z_score=c_quote.get("z_score", 0.0),
                is_outlier=c_quote.get("is_outlier", False),
                cleaned_at=datetime.utcnow()
            )
            clean_db_objects.append(clean_obj)

        self.db.bulk_save_objects(clean_db_objects)

        # 4. Persist Rejected Quotes with Rejection Reasons
        rejected_db_objects = []
        for r_item in rejected_quotes:
            raw_q = r_item["raw_quote"]
            rej_obj = RejectedObservation(
                rejection_id=str(uuid.uuid4()),
                raw_observation_id=raw_q.get("observation_id"),
                timestamp=datetime.utcnow(),
                search_date=raw_q.get("search_date"),
                route=raw_q.get("route"),
                airline=raw_q.get("airline"),
                source=raw_q.get("source"),
                base_fare=raw_q.get("base_fare"),
                total_fare=raw_q.get("total_fare"),
                rejection_reason=r_item["rejection_reason"],
                rejection_details=r_item.get("rejection_details"),
                rejected_at=datetime.utcnow()
            )
            rejected_db_objects.append(rej_obj)

        self.db.bulk_save_objects(rejected_db_objects)
        self.db.commit()

        # 5. Update ScrapeRun record
        scrape_run.finished_at = datetime.utcnow()
        scrape_run.status = "COMPLETED" if error_count == 0 else "PARTIAL"
        scrape_run.sources_attempted = sources_attempted
        scrape_run.records_collected = len(raw_observations)
        scrape_run.records_rejected = len(rejected_quotes)
        scrape_run.records_cleaned = len(clean_quotes)
        scrape_run.error_count = error_count
        self.db.commit()

        # 6. Recalculate Index for target date
        base_dt = date.fromisoformat(BASE_PERIOD_DATE)
        index_engine = APIxIndexEngine(self.db)
        index_res = index_engine.calculate_daily_index(target_date=search_date, base_date=base_dt, persist=True)

        return {
            "run_id": run_id,
            "status": scrape_run.status,
            "records_collected": len(raw_observations),
            "records_cleaned": len(clean_quotes),
            "records_rejected": len(rejected_quotes),
            "apix_value": index_res["apix_value"],
            "message": f"Successfully completed collection run. Collected {len(raw_observations)} quotes, cleaned {len(clean_quotes)}, rejected {len(rejected_quotes)}."
        }
