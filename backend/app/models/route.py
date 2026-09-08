from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from backend.app.models.base import Base

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_code = Column(String(16), unique=True, index=True, nullable=False)
    origin = Column(String(3), index=True, nullable=False)
    destination = Column(String(3), index=True, nullable=False)
    origin_city = Column(String(64), nullable=False)
    destination_city = Column(String(64), nullable=False)
    weight = Column(Float, default=0.1, nullable=False)  # DEMO_WEIGHTS
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "route_code": self.route_code,
            "origin": self.origin,
            "destination": self.destination,
            "origin_city": self.origin_city,
            "destination_city": self.destination_city,
            "weight": self.weight,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
