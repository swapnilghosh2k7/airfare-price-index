from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text
from backend.app.models.base import Base

class DataCollectionRun(Base):
    __tablename__ = "data_collection_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    source = Column(String(64), index=True, nullable=False)
    routes_requested = Column(Integer, default=0, nullable=False)
    quotes_collected = Column(Integer, default=0, nullable=False)
    quotes_valid = Column(Integer, default=0, nullable=False)
    quotes_rejected = Column(Integer, default=0, nullable=False)
    
    status = Column(String(32), default="RUNNING", index=True, nullable=False)  # RUNNING, COMPLETED, FAILED
    error_summary = Column(Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "source": self.source,
            "routes_requested": self.routes_requested,
            "quotes_collected": self.quotes_collected,
            "quotes_valid": self.quotes_valid,
            "quotes_rejected": self.quotes_rejected,
            "status": self.status,
            "error_summary": self.error_summary
        }
