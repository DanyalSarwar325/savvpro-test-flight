from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database import get_db
from backend.main import app
from backend.models import Base, Flight


@pytest.fixture(scope="function")
def client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def sample_flight(client):
    db_gen = app.dependency_overrides[get_db]()
    db = next(db_gen)
    try:
        flight = Flight(
            flight_number="FH-001",
            origin="Karachi",
            destination="Lahore",
            departure_time=datetime(2025, 6, 1, 8, 0, 0),
            duration_minutes=75,
            price=120.0,
            total_seats=2,
            seats_available=2,
        )
        db.add(flight)
        db.commit()
        db.refresh(flight)
        return flight
    finally:
        db.close()
