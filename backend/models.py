from __future__ import annotations
from datetime import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Flight(Base):
    __tablename__ = "flights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    flight_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    origin: Mapped[str] = mapped_column(String(100), nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)
    departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    seats_available: Mapped[int] = mapped_column(Integer, nullable=False)

    bookings: Mapped[List["Booking"]] = relationship(
        "Booking",
        back_populates="flight",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover - simple helper
        return (
            f"<Flight(id={self.id!r}, flight_number={self.flight_number!r}, "
            f"origin={self.origin!r}, destination={self.destination!r})>"
        )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_reference: Mapped[str] = mapped_column(String(12), nullable=False, unique=True)
    flight_id: Mapped[int] = mapped_column(Integer, ForeignKey("flights.id"), nullable=False)
    passenger_name: Mapped[str] = mapped_column(String(200), nullable=False)
    passport_number: Mapped[str] = mapped_column(String(50), nullable=False)
    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    flight: Mapped[Flight] = relationship("Flight", back_populates="bookings")

    def __repr__(self) -> str:  # pragma: no cover - simple helper
        return (
            f"<Booking(id={self.id!r}, booking_reference={self.booking_reference!r}, "
            f"passenger={self.passenger_name!r}, status={self.status!r})>"
        )
