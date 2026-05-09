from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Flight
from backend.schemas import FlightCreate, FlightResponse


router = APIRouter(prefix="/flights", tags=["Flights"])


# Return every flight currently stored in the database.
@router.get("", response_model=list[FlightResponse])
def get_flights(db: Session = Depends(get_db)):
    result = db.execute(select(Flight))
    return result.scalars().all()


# Create a new flight and initialize available seats from total seats.
@router.post("", response_model=FlightResponse, status_code=status.HTTP_201_CREATED)
def create_flight(flight_data: FlightCreate, db: Session = Depends(get_db)):
    existing_flight = db.execute(
        select(Flight).where(Flight.flight_number == flight_data.flight_number)
    ).scalar_one_or_none()
    if existing_flight is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Flight number {flight_data.flight_number} already exists.",
        )

    flight_data.seats_available = flight_data.total_seats
    flight = Flight(**flight_data.model_dump())
    db.add(flight)
    db.commit()
    db.refresh(flight)
    return flight


# Search flights by origin, destination, or departure date.
@router.get("/search", response_model=list[FlightResponse])
def search_flights(
    origin: str | None = None,
    destination: str | None = None,
    date: str | None = None,
    db: Session = Depends(get_db),
):
    if origin is None and destination is None and date is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one search parameter: origin, destination, date.",
        )

    query = select(Flight)

    if origin is not None:
        query = query.where(Flight.origin.ilike(origin))
    if destination is not None:
        query = query.where(Flight.destination.ilike(destination))
    if date is not None:
        query = query.where(Flight.departure_time.like(f"{date}%"))

    flights = db.execute(query).scalars().all()
    if not flights:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No flights found matching the given criteria.",
        )

    return flights
