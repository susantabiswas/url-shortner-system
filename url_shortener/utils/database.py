from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from url_shortener.config import get_settings

engine = create_engine(
    get_settings().db_url,
    connect_args={"check_same_thread": False}  # Only req for sqlite
)

# default db session settings
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db() -> Session:
    """Get a db session instance of :class:`Session`.

    Yields:
        db: instance of :class:`Session`
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
