import hashlib
from datetime import datetime, date
from typing import Dict, Any, Union, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.app.models.base import Base
from backend.app.models.fare_quote import FareQuote
from backend.app.core.config import settings

engine_kwargs = {}
db_url = settings.database_url
if db_url.startswith('sqlite'):
    engine_kwargs['connect_args'] = {'check_same_thread': False}

engine = create_engine(db_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    # Check and add columns to existing SQLite table if not present
    try:
        with engine.connect() as conn:
            # Check existing columns
            res = conn.exec_driver_sql("PRAGMA table_info(fare_quotes)").fetchall()
            cols = [r[1] for r in res]
            if "source_type" not in cols:
                conn.exec_driver_sql("ALTER TABLE fare_quotes ADD COLUMN source_type VARCHAR(32) DEFAULT 'airline_direct'")
            if "seats_remaining" not in cols:
                conn.exec_driver_sql("ALTER TABLE fare_quotes ADD COLUMN seats_remaining INTEGER")
            conn.commit()
    except Exception:
        pass

def get_session() -> Session:
    return SessionLocal()

def compute_raw_hash(data: Dict[str, Any]) -> str:
    origin = data.get('origin', '')
    destination = data.get('destination', '')
    dep_date = data.get('departure_date', '')
    carrier = data.get('carrier', '')
    flight_num = data.get('flight_number', '')
    fare_class = data.get('fare_class', 'Economy')
    source = data.get('source', '')
    obs = data.get('observation_timestamp', datetime.utcnow().isoformat())
    payload = f'{origin}|{destination}|{dep_date}|{carrier}|{flight_num}|{fare_class}|{source}|{obs}'
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

def save_fare_quote(quote_data: Union[FareQuote, Dict[str, Any]], session: Optional[Session] = None) -> FareQuote:
    init_db()
    own_session = False
    if session is None:
        session = SessionLocal()
        own_session = True

    try:
        if isinstance(quote_data, FareQuote):
            obj = quote_data
            if not obj.source_type:
                obj.source_type = 'airline_direct'
            if not obj.raw_hash:
                obj.raw_hash = compute_raw_hash(obj.to_dict())
        else:
            data = dict(quote_data)
            if 'source_type' not in data or not data['source_type']:
                data['source_type'] = 'airline_direct'
            
            # parse dates if strings
            dep_date = data.get('departure_date')
            if isinstance(dep_date, str):
                data['departure_date'] = datetime.strptime(dep_date, '%Y-%m-%d').date()
            elif isinstance(dep_date, datetime):
                data['departure_date'] = dep_date.date()
                
            obs_dt = data.get('observation_timestamp')
            if isinstance(obs_dt, str):
                try:
                    data['observation_timestamp'] = datetime.fromisoformat(obs_dt)
                except Exception:
                    data['observation_timestamp'] = datetime.utcnow()
            elif not obs_dt:
                data['observation_timestamp'] = datetime.utcnow()

            if not data.get('raw_hash'):
                data['raw_hash'] = compute_raw_hash(data)

            obj = FareQuote(**data)

        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
    except Exception as e:
        session.rollback()
        raise e
    finally:
        if own_session:
            session.close()

__all__ = ['Base', 'FareQuote', 'engine', 'SessionLocal', 'init_db', 'get_session', 'save_fare_quote', 'compute_raw_hash']
