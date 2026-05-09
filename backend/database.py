from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///flighthub.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, future=True
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)


def get_db() -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create tables (safe to call on import/startup)
Base.metadata.create_all(bind=engine)
