"""
Database Connection and Session Management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session
from backend.config import DATABASE_URL

# SQLite requires check_same_thread=False for multi-threaded/async FastAPI usage
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    future=True
)

SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionLocal = scoped_session(SessionFactory)
Base = declarative_base()

def get_db():
    """FastAPI Dependency for obtaining DB sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes all database tables"""
    import backend.models.db_models  # Ensure models are loaded
    Base.metadata.create_all(bind=engine)
