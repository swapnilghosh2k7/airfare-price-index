import pytest
from datetime import datetime, date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import (
    Base, Route, Carrier, FareQuote, DataQualityRecord, IndexObservation, DataCollectionRun
)

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_route_model(db_session):
    route = Route(
        route_code="DEL-BOM",
        origin="DEL",
        destination="BOM",
        origin_city="Delhi",
        destination_city="Mumbai",
        weight=0.18,
        active=True
    )
    db_session.add(route)
    db_session.commit()

    saved_route = db_session.query(Route).filter_by(route_code="DEL-BOM").first()
    assert saved_route is not None
    assert saved_route.origin == "DEL"
    assert saved_route.weight == 0.18
    assert "DEL-BOM" in str(saved_route.to_dict()["route_code"])

def test_carrier_model(db_session):
    carrier = Carrier(name="IndiGo", iata_code="6E", source_type="LCC", active=True)
    db_session.add(carrier)
    db_session.commit()

    saved = db_session.query(Carrier).filter_by(iata_code="6E").first()
    assert saved is not None
    assert saved.name == "IndiGo"

def test_fare_quote_and_quality(db_session):
    fare = FareQuote(
        observation_timestamp=datetime.utcnow(),
        origin="DEL",
        destination="BOM",
        departure_date=date(2026, 9, 10),
        lead_time_days=7,
        carrier="IndiGo",
        flight_number="6E-101",
        fare_class="Economy",
        base_fare=5000.0,
        taxes=1200.0,
        total_fare=6200.0,
        currency="INR",
        source="mock_provider",
        raw_hash="hash12345"
    )
    db_session.add(fare)
    db_session.commit()

    quality = DataQualityRecord(
        fare_quote_id=fare.id,
        quality_score=95.0,
        outlier_flag=False,
        duplicate_flag=False
    )
    db_session.add(quality)
    db_session.commit()

    assert fare.id is not None
    assert quality.fare_quote_id == fare.id

def test_index_observation(db_session):
    idx = IndexObservation(
        observation_date=date(2026, 9, 3),
        route_code="DEL-BOM",
        lead_time_bucket=7,
        route_index=105.4,
        national_index=103.2,
        base_period="2026-08-BASE30",
        weight=0.18,
        sample_count=24
    )
    db_session.add(idx)
    db_session.commit()

    saved = db_session.query(IndexObservation).filter_by(route_code="DEL-BOM").first()
    assert saved is not None
    assert saved.route_index == 105.4
