import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Booking, Flight
from backend.schemas import BookingCreate, BookingResponse, CancelResponse


router = APIRouter(prefix="/bookings", tags=["Bookings"])


def generate_reference() -> str:
    """Generate a booking reference in the format FH-XXXXXX."""
    return "FH-" + uuid.uuid4().hex[:6].upper()


# Create a new booking with atomicity guarantees on seat availability checks.
@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(booking_data: BookingCreate, db: Session = Depends(get_db)):
    flight = db.execute(
        select(Flight).where(Flight.id == booking_data.flight_id)
    ).scalar_one_or_none()
    if flight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found.",
        )

    if flight.seats_available <= 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No seats available on this flight.",
        )

    existing_seat = db.execute(
        select(Booking).where(
            Booking.flight_id == booking_data.flight_id,
            Booking.seat_number == booking_data.seat_number,
            Booking.status == "confirmed",
        )
    ).scalar_one_or_none()
    if existing_seat is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Seat {booking_data.seat_number} is already taken on this flight.",
        )

    booking_reference = generate_reference()
    flight.seats_available -= 1
    booking = Booking(
        booking_reference=booking_reference,
        flight_id=booking_data.flight_id,
        passenger_name=booking_data.passenger_name,
        passport_number=booking_data.passport_number,
        seat_number=booking_data.seat_number,
        status="confirmed",
    )
    db.add(booking)
    db.commit()
    db.refresh(flight)
    db.refresh(booking)
    return booking


# Search bookings by passenger name or booking reference.
@router.get("", response_model=list[BookingResponse])
def get_bookings(
    name: str | None = None,
    ref: str | None = None,
    db: Session = Depends(get_db),
):
    if name is None and ref is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide at least one search parameter: name or ref.",
        )

    query = select(Booking)

    if ref is not None:
        query = query.where(Booking.booking_reference == ref)
    elif name is not None:
        query = query.where(Booking.passenger_name.ilike(f"%{name}%"))

    bookings = db.execute(query).scalars().all()
    if not bookings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No bookings found.",
        )

    return bookings


# Cancel a booking by its reference and restore the seat to the flight.
@router.delete("/{reference}", response_model=CancelResponse)
def cancel_booking(reference: str, db: Session = Depends(get_db)):
    booking = db.execute(
        select(Booking).where(Booking.booking_reference == reference)
    ).scalar_one_or_none()
    if booking is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking {reference} not found.",
        )

    if booking.status == "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking {reference} is already cancelled.",
        )

    booking.status = "cancelled"
    flight = db.execute(
        select(Flight).where(Flight.id == booking.flight_id)
    ).scalar_one_or_none()
    if flight is not None:
        flight.seats_available += 1

    db.commit()
    db.refresh(booking)
    if flight is not None:
        db.refresh(flight)

    return CancelResponse(
        booking_reference=reference,
        status="cancelled",
        message=f"Booking {reference} has been successfully cancelled.",
    )
