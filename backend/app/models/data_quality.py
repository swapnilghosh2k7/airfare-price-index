from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
from backend.app.models.base import Base

class DataQualityRecord(Base):
    __tablename__ = "data_quality_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fare_quote_id = Column(Integer, ForeignKey("fare_quotes.id"), index=True, nullable=False)
    
    quality_score = Column(Float, default=100.0, nullable=False)  # 0.0 to 100.0
    missing_fields = Column(Text, default="[]", nullable=False)  # JSON string
    outlier_flag = Column(Boolean, default=False, index=True, nullable=False)
    duplicate_flag = Column(Boolean, default=False, index=True, nullable=False)
    validation_errors = Column(Text, default="[]", nullable=False)  # JSON string
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "fare_quote_id": self.fare_quote_id,
            "quality_score": self.quality_score,
            "missing_fields": self.missing_fields,
            "outlier_flag": self.outlier_flag,
            "duplicate_flag": self.duplicate_flag,
            "validation_errors": self.validation_errors,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
