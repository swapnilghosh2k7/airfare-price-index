from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from backend.app.models.base import Base

class Carrier(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    iata_code = Column(String(3), unique=True, index=True, nullable=False)
    source_type = Column(String(32), default="LCC", nullable=False)  # e.g., LCC or FSC
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "iata_code": self.iata_code,
            "source_type": self.source_type,
            "active": self.active,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
