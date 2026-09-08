from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.models.base import Base
# Import all models to ensure they are registered with Base metadata
import backend.app.models  # noqa: F401

engine_kwargs = {}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    try:
        with engine.connect() as conn:
            res = conn.exec_driver_sql("PRAGMA table_info(fare_quotes)").fetchall()
            cols = [r[1] for r in res]
            if "source_type" not in cols:
                conn.exec_driver_sql("ALTER TABLE fare_quotes ADD COLUMN source_type VARCHAR(32) DEFAULT 'airline_direct'")
            if "seats_remaining" not in cols:
                conn.exec_driver_sql("ALTER TABLE fare_quotes ADD COLUMN seats_remaining INTEGER")
            conn.commit()
    except Exception:
        pass

def get_db():
    """FastAPI dependency for database session management"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
