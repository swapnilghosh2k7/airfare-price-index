import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from backend.app.models import Base, IndexObservation, FareQuote, DataQualityRecord
from backend.app.analytics.advanced import AdvancedAnalyticsEngine

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Seed sample national index observations
    for i in range(10):
        obs = IndexObservation(
            observation_date=date(2026, 8, 1 + i),
            route_code="NATIONAL",
            lead_time_bucket=0,
            route_index=100.0 + (i * 0.5),
            national_index=100.0 + (i * 0.5),
            base_period="2026-08-BASE30",
            weight=1.0,
            sample_count=100
        )
        session.add(obs)

    # Seed sample route observations with surge
    for i in range(10):
        obs_route = IndexObservation(
            observation_date=date(2026, 8, 1 + i),
            route_code="DEL-BOM",
            lead_time_bucket=0,
            route_index=100.0 if i < 7 else 125.0,  # +25% surge
            national_index=100.0,
            base_period="2026-08-BASE30",
            weight=0.18,
            sample_count=50
        )
        session.add(obs_route)

    session.commit()
    yield session
    session.close()

def test_forecast_next_7_days(db_session):
    fc = AdvancedAnalyticsEngine.forecast_next_7_days(db_session)
    assert len(fc) == 7
    assert fc[0]["status"] == "EXPERIMENTAL_FORECAST"
    assert fc[0]["forecast_index"] >= 100.0

def test_generate_alerts(db_session):
    alerts = AdvancedAnalyticsEngine.generate_alerts_and_anomalies(db_session)
    assert len(alerts) >= 1
    assert alerts[0]["route_code"] == "DEL-BOM"
    assert alerts[0]["type"] == "PRICE_SURGE_ALERT"

def test_demand_proxy(db_session):
    proxy = AdvancedAnalyticsEngine.calculate_demand_proxy_index(db_session)
    assert "demand_pressure_score" in proxy
    assert "status" in proxy
