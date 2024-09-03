from sqlalchemy import create_engine, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from url_shortener.config import get_settings
from typing import Annotated


class DatabaseManager:
    """Class to manage the database connection setup.
    """
    # Base class for ORM models. When a class inherits this class, 
    # sqlAlchemy knows that it is an ORM model and it should be 
    # mapped to a table in the DB.
    Base = declarative_base()

    def __init__(
        self,
        db_url: str,
        pool_size: int = 5,
        pool_recycle: int = 3600,
        isolation_level: str = "SERIALIZABLE",
        connect_args: dict = {}
    ) -> None:

        # Create a new engine instance.Engine is a way to interact with the DB.
        self.engine = create_engine(
            db_url,
            pool_size=pool_size,
            pool_recycle=pool_recycle,
            isolation_level=isolation_level,
            connect_args=connect_args
        )

        # This is a factory which creates a new SqlAlchemy session.
        # Session is not a separate connection but rather a logical isolation
        # for a request to interact with DB. Behind the scenes it asks for a
        # connection from sqlAlchemy's connection pool.
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.get_engine()
        )

    def get_engine(self) -> Engine:
        return self.engine

    def get_session(self) -> Session:
        return self.SessionLocal()

    def create_tables(self) -> None:
        DatabaseManager.Base.metadata.create_all(bind=self.get_engine())


# Required for creating ORM classes
Base = DatabaseManager.Base

# Create the instance for exporting
db_manager = DatabaseManager(
    get_settings().db_url,
    connect_args={"check_same_thread": False})
