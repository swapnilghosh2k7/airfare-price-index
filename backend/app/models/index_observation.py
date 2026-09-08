from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from backend.app.models.base import Base

class IndexObservation(Base):
    __tablename__ = "index_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    observation_date = Column(Date, index=True, nullable=False)
    
    route_code = Column(String(16), index=True, nullable=False)  # e.g., "DEL-BOM" or "NATIONAL"
    lead_time_bucket = Column(Integer, index=True, default=0, nullable=False)  # 0 for ALL, or 1,7,15,30,45
    
    route_index = Column(Float, default=100.0, nullable=False)
    national_index = Column(Float, default=100.0, nullable=False)
    
    base_period = Column(String(64), default="2026-08-BASE30", nullable=False)
    weight = Column(Float, default=1.0, nullable=False)
    sample_count = Column(Integer, default=0, nullable=False)
    
    methodology_version = Column(String(32), default="APIX_v1", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "observation_date": self.observation_date.isoformat() if self.observation_date else None,
            "route_code": self.route_code,
            "lead_time_bucket": self.lead_time_bucket,
            "route_index": self.route_index,
            "national_index": self.national_index,
            "base_period": self.base_period,
            "weight": self.weight,
            "sample_count": self.sample_count,
            "methodology_version": self.methodology_version,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
