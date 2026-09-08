from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey
from backend.app.models.base import Base

class FareQuote(Base):
    __tablename__ = "fare_quotes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    observation_timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    
    origin = Column(String(3), index=True, nullable=False)
    destination = Column(String(3), index=True, nullable=False)
    
    departure_date = Column(Date, index=True, nullable=False)
    lead_time_days = Column(Integer, index=True, nullable=False)  # 1, 7, 15, 30, 45
    
    carrier = Column(String(64), index=True, nullable=False)
    flight_number = Column(String(32), nullable=False)
    
    fare_class = Column(String(32), default="Economy", nullable=False)
    
    base_fare = Column(Float, default=0.0, nullable=False)
    taxes = Column(Float, default=0.0, nullable=False)
    airport_fee = Column(Float, default=0.0, nullable=False)
    fuel_surcharge = Column(Float, default=0.0, nullable=False)
    user_development_fee = Column(Float, default=0.0, nullable=False)
    convenience_fee = Column(Float, default=0.0, nullable=False)
    other_fee = Column(Float, default=0.0, nullable=False)
    
    total_fare = Column(Float, index=True, nullable=False)
    currency = Column(String(3), default="INR", nullable=False)
    
    source = Column(String(64), index=True, nullable=False)  # mock_provider, dataset_provider, live
    source_type = Column(String(32), default="airline_direct", nullable=True)  # airline_direct, ota, mock
    source_url = Column(String(256), nullable=True)
    
    availability_status = Column(String(32), default="AVAILABLE", nullable=False)
    seats_remaining = Column(Integer, nullable=True)
    collection_status = Column(String(32), default="VALID", nullable=False)
    
    raw_hash = Column(String(64), index=True, nullable=False)  # SHA-256 fingerprint
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "observation_timestamp": self.observation_timestamp.isoformat() if self.observation_timestamp else None,
            "origin": self.origin,
            "destination": self.destination,
            "departure_date": self.departure_date.isoformat() if self.departure_date else None,
            "lead_time_days": self.lead_time_days,
            "carrier": self.carrier,
            "flight_number": self.flight_number,
            "fare_class": self.fare_class,
            "base_fare": self.base_fare,
            "taxes": self.taxes,
            "airport_fee": self.airport_fee,
            "fuel_surcharge": self.fuel_surcharge,
            "user_development_fee": self.user_development_fee,
            "convenience_fee": self.convenience_fee,
            "other_fee": self.other_fee,
            "total_fare": self.total_fare,
            "currency": self.currency,
            "source": self.source,
            "source_type": self.source_type,
            "source_url": self.source_url,
            "availability_status": self.availability_status,
            "seats_remaining": self.seats_remaining,
            "collection_status": self.collection_status,
            "raw_hash": self.raw_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
