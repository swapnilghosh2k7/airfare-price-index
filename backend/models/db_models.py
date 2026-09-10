"""
Relational Database Models for APIx Platform
"""

import uuid
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Date, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from backend.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class Route(Base):
    __tablename__ = "routes"

    route_id = Column(Integer, primary_key=True, autoincrement=True)
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    route_code = Column(String(7), unique=True, nullable=False, index=True)  # e.g. DEL-BOM
    region = Column(String(50), nullable=True)
    weight = Column(Float, nullable=False, default=0.05)  # DGCA Traffic passenger weight, sum = 1.0
    traffic_volume = Column(Integer, nullable=False, default=100000)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Airline(Base):
    __tablename__ = "airlines"

    airline_id = Column(Integer, primary_key=True, autoincrement=True)
    airline_name = Column(String(100), unique=True, nullable=False)
    iata_code = Column(String(3), unique=True, nullable=False)
    tier = Column(String(10), nullable=False, default="LCC")  # LCC or FSC
    market_share = Column(Float, nullable=False, default=0.10)
    is_active = Column(Boolean, default=True, nullable=False)

class Source(Base):
    __tablename__ = "sources"

    source_id = Column(Integer, primary_key=True, autoincrement=True)
    source_name = Column(String(100), unique=True, nullable=False)
    source_type = Column(String(20), nullable=False)  # AIRLINE or OTA
    domain = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=True, nullable=False)
    robots_allowed = Column(Boolean, default=True, nullable=False)
    rate_limit_rps = Column(Float, default=1.0)
    status = Column(String(20), default="LIVE")  # LIVE, MOCK, UNAVAILABLE, ERROR
    last_scrape_at = Column(DateTime, nullable=True)
    captcha_detected_count = Column(Integer, default=0)
    requests_successful = Column(Integer, default=0)
    requests_failed = Column(Integer, default=0)
    records_collected = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)

class FareObservationRaw(Base):
    __tablename__ = "fare_observations_raw"

    observation_id = Column(String(36), primary_key=True, default=generate_uuid)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    search_date = Column(Date, nullable=False, index=True)
    travel_date = Column(Date, nullable=False, index=True)
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    route = Column(String(7), nullable=False, index=True)
    airline = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    source_type = Column(String(20), nullable=False)  # AIRLINE or OTA
    flight_number = Column(String(20), nullable=False)
    departure_time = Column(String(10), nullable=True)
    arrival_time = Column(String(10), nullable=True)
    duration = Column(String(20), nullable=True)
    stops = Column(Integer, default=0)
    fare_class = Column(String(30), default="Economy")
    refundable = Column(Boolean, default=False)
    
    # Fare breakdown components
    base_fare = Column(Float, nullable=False)
    taxes = Column(Float, nullable=False)
    airport_fee = Column(Float, default=0.0)
    user_development_fee = Column(Float, default=0.0)
    convenience_fee = Column(Float, default=0.0)
    fuel_surcharge = Column(Float, default=0.0)
    total_fare = Column(Float, nullable=False)
    currency = Column(String(5), default="INR")
    
    advance_purchase_days = Column(Integer, nullable=False, index=True)  # 1, 7, 15, 30, 45
    availability_status = Column(String(30), default="AVAILABLE")
    scrape_status = Column(String(20), default="SUCCESS")
    scrape_run_id = Column(String(36), nullable=True, index=True)

    __table_args__ = (
        Index("idx_raw_route_date_win", "route", "search_date", "advance_purchase_days"),
    )

class FareObservationClean(Base):
    __tablename__ = "fare_observations_clean"

    clean_id = Column(String(36), primary_key=True, default=generate_uuid)
    raw_observation_id = Column(String(36), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    search_date = Column(Date, nullable=False, index=True)
    travel_date = Column(Date, nullable=False, index=True)
    origin = Column(String(3), nullable=False, index=True)
    destination = Column(String(3), nullable=False, index=True)
    route = Column(String(7), nullable=False, index=True)
    airline = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False, index=True)
    source_type = Column(String(20), nullable=False)
    flight_number = Column(String(20), nullable=False)
    departure_time = Column(String(10), nullable=True)
    arrival_time = Column(String(10), nullable=True)
    duration = Column(String(20), nullable=True)
    stops = Column(Integer, default=0)
    fare_class = Column(String(30), default="Economy")
    
    # Validated components
    base_fare = Column(Float, nullable=False)
    taxes = Column(Float, nullable=False)
    airport_fee = Column(Float, default=0.0)
    user_development_fee = Column(Float, default=0.0)
    convenience_fee = Column(Float, default=0.0)
    fuel_surcharge = Column(Float, default=0.0)
    total_fare = Column(Float, nullable=False)
    currency = Column(String(5), default="INR")
    advance_purchase_days = Column(Integer, nullable=False, index=True)
    
    # Statistical validation metadata
    z_score = Column(Float, default=0.0)
    is_outlier = Column(Boolean, default=False)
    cleaned_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_clean_route_date_win", "route", "search_date", "advance_purchase_days"),
    )

class RejectedObservation(Base):
    __tablename__ = "rejected_observations"

    rejection_id = Column(String(36), primary_key=True, default=generate_uuid)
    raw_observation_id = Column(String(36), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    search_date = Column(Date, nullable=True)
    route = Column(String(7), nullable=True)
    airline = Column(String(100), nullable=True)
    source = Column(String(100), nullable=True)
    base_fare = Column(Float, nullable=True)
    total_fare = Column(Float, nullable=True)
    rejection_reason = Column(String(100), nullable=False)  # OUTLIER_IQR, FARE_COMPONENT_MISMATCH, DUPLICATE, etc.
    rejection_details = Column(Text, nullable=True)
    rejected_at = Column(DateTime, default=datetime.utcnow)

class IndexValue(Base):
    __tablename__ = "index_values"

    index_id = Column(String(36), primary_key=True, default=generate_uuid)
    index_date = Column(Date, nullable=False, index=True)
    frequency = Column(String(10), default="DAILY", index=True)  # DAILY, WEEKLY, MONTHLY
    apix_value = Column(Float, nullable=False)  # Base 100
    base_period_fare = Column(Float, nullable=False)
    current_weighted_fare = Column(Float, nullable=False)
    price_relative = Column(Float, nullable=False)
    observation_count = Column(Integer, nullable=False)
    calculated_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_date_frequency", "index_date", "frequency", unique=True),
    )

class IndexWeight(Base):
    __tablename__ = "index_weights"

    weight_id = Column(Integer, primary_key=True, autoincrement=True)
    index_date = Column(Date, nullable=False, index=True)
    route_code = Column(String(7), nullable=False)
    route_weight = Column(Float, nullable=False)
    source_name = Column(String(100), nullable=True)
    source_weight = Column(Float, nullable=True)
    traffic_share = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow)

class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    run_id = Column(String(36), primary_key=True, default=generate_uuid)
    trigger_type = Column(String(20), default="SCHEDULED")  # SCHEDULED, MANUAL
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="RUNNING")  # RUNNING, COMPLETED, FAILED, PARTIAL
    sources_attempted = Column(Integer, default=0)
    records_collected = Column(Integer, default=0)
    records_rejected = Column(Integer, default=0)
    records_cleaned = Column(Integer, default=0)
    error_count = Column(Integer, default=0)

class ScrapeError(Base):
    __tablename__ = "scrape_errors"

    error_id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(36), nullable=True, index=True)
    source_name = Column(String(100), nullable=False)
    error_type = Column(String(50), nullable=False)  # CAPTCHA_DETECTED, ROBOTS_DENIED, TIMEOUT, RATE_LIMIT, HTTP_ERROR
    status_code = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=False)
    url = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

class BacktestResult(Base):
    __tablename__ = "backtest_results"

    backtest_id = Column(String(36), primary_key=True, default=generate_uuid)
    run_date = Column(Date, nullable=False, index=True)
    target_date = Column(Date, nullable=False, index=True)
    apix_value = Column(Float, nullable=False)
    dgca_benchmark_fare = Column(Float, nullable=False)
    dgca_benchmark_index = Column(Float, nullable=False)
    absolute_error = Column(Float, nullable=False)
    percentage_error = Column(Float, nullable=False)
    is_benchmark_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
