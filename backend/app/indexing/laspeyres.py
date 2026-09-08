import logging
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models import Route, FareQuote, DataQualityRecord, IndexObservation

logger = logging.getLogger("airfarex.indexing")

class LaspeyresIndexCalculator:
    METHODOLOGY_VERSION = "APIX_v1"
    
    @staticmethod
    def calculate_route_index(p_current: float, p_base: float) -> float:
        """Calculates single route index: I = (P_t / P_0) * 100"""
        if p_base <= 0:
            return 100.0
        return round((p_current / p_base) * 100.0, 4)

    @staticmethod
    def calculate_national_index(route_indices: Dict[str, float], route_weights: Dict[str, float]) -> float:
        """
        Calculates weighted aggregate National APIx Index:
        APIx = Sum(w_i * I_i) / Sum(w_i)
        """
        if not route_indices or not route_weights:
            return 100.0

        total_weight = 0.0
        weighted_sum = 0.0

        for r_code, idx_val in route_indices.items():
            w = route_weights.get(r_code, 0.0)
            if w > 0:
                weighted_sum += w * idx_val
                total_weight += w

        if total_weight <= 0:
            return 100.0

        return round(weighted_sum / total_weight, 4)

    @classmethod
    def compute_base_period_medians(cls, db: Session, base_period_code: str = "2026-08-BASE30") -> Dict[Tuple[str, int], float]:
        """
        Computes P_{i,0,l} median baseline fares over all observations in the dataset
        grouped by (route_code, lead_time_days).
        """
        query = (
            db.query(
                FareQuote.origin,
                FareQuote.destination,
                FareQuote.lead_time_days,
                FareQuote.total_fare
            )
            .join(DataQualityRecord, DataQualityRecord.fare_quote_id == FareQuote.id)
            .filter(
                FareQuote.collection_status == "VALID",
                DataQualityRecord.outlier_flag == False,
                FareQuote.total_fare > 0
            )
        )
        
        df = pd.read_sql(query.statement, db.bind)
        if df.empty:
            logger.warning("No valid fare quotes found for base period median calculation.")
            return {}

        df["route_code"] = df["origin"] + "-" + df["destination"]
        
        medians = {}
        for (r_code, lead), group in df.groupby(["route_code", "lead_time_days"]):
            med = float(group["total_fare"].median())
            medians[(r_code, lead)] = med

        return medians

    @classmethod
    def build_full_index_series(cls, db: Session, base_period_code: str = "2026-08-BASE30") -> List[IndexObservation]:
        """
        Processes all historical dates in DB, computing daily route indices & national APIx observations.
        """
        # 1. Fetch active routes & normalized weights
        active_routes = db.query(Route).filter_by(active=True).all()
        if not active_routes:
            logger.error("No active routes found in database.")
            return []

        route_weights = {r.route_code: r.weight for r in active_routes}
        total_w = sum(route_weights.values())
        if total_w > 0:
            route_weights = {k: v / total_w for k, v in route_weights.items()}

        # 2. Compute Base Period Medians P_0
        base_medians = cls.compute_base_period_medians(db, base_period_code=base_period_code)
        if not base_medians:
            logger.error("Base period medians could not be computed.")
            return []

        # 3. Load valid daily observations
        query = (
            db.query(
                FareQuote.observation_timestamp,
                FareQuote.origin,
                FareQuote.destination,
                FareQuote.lead_time_days,
                FareQuote.total_fare
            )
            .join(DataQualityRecord, DataQualityRecord.fare_quote_id == FareQuote.id)
            .filter(
                FareQuote.collection_status == "VALID",
                DataQualityRecord.outlier_flag == False,
                FareQuote.total_fare > 0
            )
        )
        
        df = pd.read_sql(query.statement, db.bind)
        if df.empty:
            return []

        df["route_code"] = df["origin"] + "-" + df["destination"]
        df["obs_date"] = pd.to_datetime(df["observation_timestamp"]).dt.date

        unique_dates = sorted(df["obs_date"].unique())
        
        index_records = []
        
        # Clear existing observations for fresh build
        db.query(IndexObservation).delete()
        db.commit()

        for obs_d in unique_dates:
            day_df = df[df["obs_date"] == obs_d]
            daily_route_indices = {}
            
            # Compute lead-time bucket indices per route
            for r_code in route_weights.keys():
                route_df = day_df[day_df["route_code"] == r_code]
                if route_df.empty:
                    continue
                
                lead_indices = []
                total_samples = 0
                
                for lead_time in [1, 7, 15, 30, 45]:
                    lead_df = route_df[route_df["lead_time_days"] == lead_time]
                    if lead_df.empty:
                        continue
                        
                    p_t = float(lead_df["total_fare"].median())
                    p_0 = base_medians.get((r_code, lead_time), p_t)
                    
                    sub_idx = cls.calculate_route_index(p_t, p_0)
                    lead_indices.append(sub_idx)
                    samples = len(lead_df)
                    total_samples += samples
                    
                    # Store Lead-Time Bucket specific IndexObservation
                    rec_lead = IndexObservation(
                        observation_date=obs_d,
                        route_code=r_code,
                        lead_time_bucket=lead_time,
                        route_index=sub_idx,
                        national_index=100.0,  # placeholder, calculated below
                        base_period=base_period_code,
                        weight=route_weights.get(r_code, 0.1),
                        sample_count=samples,
                        methodology_version=cls.METHODOLOGY_VERSION
                    )
                    index_records.append(rec_lead)
                    
                if lead_indices:
                    composite_route_idx = float(np.mean(lead_indices))
                    daily_route_indices[r_code] = composite_route_idx
                    
                    # Store Route Composite (Bucket 0 = ALL) IndexObservation
                    rec_route_comp = IndexObservation(
                        observation_date=obs_d,
                        route_code=r_code,
                        lead_time_bucket=0,  # 0 denotes composite across all lead windows
                        route_index=composite_route_idx,
                        national_index=100.0,
                        base_period=base_period_code,
                        weight=route_weights.get(r_code, 0.1),
                        sample_count=total_samples,
                        methodology_version=cls.METHODOLOGY_VERSION
                    )
                    index_records.append(rec_route_comp)

            # Compute National Aggregate APIx Index for this date
            national_apix = cls.calculate_national_index(daily_route_indices, route_weights)
            
            # Store National Aggregate Index Observation (route_code = "NATIONAL")
            total_day_samples = len(day_df)
            rec_national = IndexObservation(
                observation_date=obs_d,
                route_code="NATIONAL",
                lead_time_bucket=0,
                route_index=national_apix,
                national_index=national_apix,
                base_period=base_period_code,
                weight=1.0,
                sample_count=total_day_samples,
                methodology_version=cls.METHODOLOGY_VERSION
            )
            index_records.append(rec_national)
            
            # Update national_index field in day's records
            for r in index_records:
                if r.observation_date == obs_d:
                    r.national_index = national_apix

        db.bulk_save_objects(index_records)
        db.commit()
        logger.info(f"Successfully generated {len(index_records)} index observations across {len(unique_dates)} dates.")
        return index_records
