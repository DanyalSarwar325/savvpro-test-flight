"""
FastAPI application entry point for FlightHub.
Run with: uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend.models import Base
from backend.routers import bookings, flights


app = FastAPI(
    title="FlightHub API",
    description="Flight search and booking system for travel agency staff",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flights.router)
app.include_router(bookings.router)


@app.get("/")
def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "FlightHub API is running"}


@app.on_event("startup")
def startup_event():
    """Ensure database tables exist on application startup."""
    Base.metadata.create_all(bind=engine)
