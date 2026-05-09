from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _strip_string(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    return value


# Shared flight fields used when creating and returning flight data.
class FlightBase(BaseModel):
    origin: str
    destination: str
    departure_time: datetime
    duration_minutes: int = Field(gt=0)
    price: float = Field(gt=0)
    total_seats: int = Field(gt=0)

    @field_validator("origin", "destination", mode="before")
    @classmethod
    def strip_flight_strings(cls, value: object) -> object:
        return _strip_string(value)


# Request schema for creating a new flight record.
class FlightCreate(FlightBase):
    flight_number: str
    seats_available: int | None = None

    @field_validator("flight_number", mode="before")
    @classmethod
    def strip_flight_number(cls, value: object) -> object:
        return _strip_string(value)

    @model_validator(mode="after")
    def set_seats_available(self) -> "FlightCreate":
        self.seats_available = self.total_seats
        return self


# Response schema for serializing flight records from SQLAlchemy ORM objects.
class FlightResponse(FlightBase):
    id: int
    flight_number: str
    seats_available: int

    model_config = ConfigDict(from_attributes=True)

    @field_validator("origin", "destination", "flight_number", mode="before")
    @classmethod
    def strip_flight_response_strings(cls, value: object) -> object:
        return _strip_string(value)


# Request schema for creating a new booking.
class BookingCreate(BaseModel):
    flight_id: int
    passenger_name: str = Field(min_length=2)
    passport_number: str = Field(min_length=5, max_length=50)
    seat_number: str = Field(min_length=1, max_length=10)

    @field_validator("passenger_name", "passport_number", "seat_number", mode="before")
    @classmethod
    def strip_booking_strings(cls, value: object) -> object:
        return _strip_string(value)


# Response schema for serializing a booking with its nested flight details.
class BookingResponse(BaseModel):
    booking_reference: str
    flight_id: int
    passenger_name: str
    passport_number: str
    seat_number: str
    status: str
    created_at: datetime
    flight: FlightResponse

    model_config = ConfigDict(from_attributes=True)

    @field_validator(
        "booking_reference",
        "passenger_name",
        "passport_number",
        "seat_number",
        "status",
        mode="before",
    )
    @classmethod
    def strip_booking_response_strings(cls, value: object) -> object:
        return _strip_string(value)


# Response schema for confirming a booking cancellation.
class CancelResponse(BaseModel):
    booking_reference: str
    status: str
    message: str

    @field_validator("booking_reference", "status", "message", mode="before")
    @classmethod
    def strip_cancel_strings(cls, value: object) -> object:
        return _strip_string(value)
