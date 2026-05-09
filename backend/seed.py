"""
Seed script to populate the flights table with sample data.
Run with: python -m backend.seed
"""
from datetime import datetime, timedelta

from sqlalchemy import select

from backend.database import SessionLocal, engine
from backend.models import Flight


def seed_flights():
    """Populate the flights table with 12 realistic sample flights."""
    db = SessionLocal()
    
    try:
        existing_flights = db.execute(select(Flight)).scalar_one_or_none()
        if existing_flights is not None:
            print("Database already seeded.")
            return
        
        flights_data = [
            {
                "flight_number": "FH-101",
                "origin": "Karachi",
                "destination": "Lahore",
                "departure_time": datetime(2025, 6, 5, 7, 30),
                "duration_minutes": 120,
                "price": 100.0,
                "total_seats": 80,
            },
            {
                "flight_number": "FH-102",
                "origin": "Lahore",
                "destination": "Islamabad",
                "departure_time": datetime(2025, 6, 8, 9, 0),
                "duration_minutes": 90,
                "price": 90.0,
                "total_seats": 60,
            },
            {
                "flight_number": "FH-103",
                "origin": "Islamabad",
                "destination": "Karachi",
                "departure_time": datetime(2025, 6, 12, 14, 15),
                "duration_minutes": 120,
                "price": 110.0,
                "total_seats": 75,
            },
            {
                "flight_number": "FH-104",
                "origin": "Karachi",
                "destination": "Dubai",
                "departure_time": datetime(2025, 6, 15, 11, 45),
                "duration_minutes": 240,
                "price": 300.0,
                "total_seats": 100,
            },
            {
                "flight_number": "FH-105",
                "origin": "Lahore",
                "destination": "London",
                "departure_time": datetime(2025, 6, 20, 22, 30),
                "duration_minutes": 480,
                "price": 800.0,
                "total_seats": 120,
            },
            {
                "flight_number": "FH-106",
                "origin": "Islamabad",
                "destination": "New York",
                "departure_time": datetime(2025, 6, 25, 1, 0),
                "duration_minutes": 600,
                "price": 900.0,
                "total_seats": 100,
            },
            {
                "flight_number": "FH-107",
                "origin": "Karachi",
                "destination": "Islamabad",
                "departure_time": datetime(2025, 7, 2, 8, 0),
                "duration_minutes": 90,
                "price": 95.0,
                "total_seats": 65,
            },
            {
                "flight_number": "FH-108",
                "origin": "Dubai",
                "destination": "Karachi",
                "departure_time": datetime(2025, 7, 5, 16, 30),
                "duration_minutes": 240,
                "price": 320.0,
                "total_seats": 95,
            },
            {
                "flight_number": "FH-109",
                "origin": "London",
                "destination": "Lahore",
                "departure_time": datetime(2025, 7, 10, 10, 15),
                "duration_minutes": 480,
                "price": 850.0,
                "total_seats": 110,
            },
            {
                "flight_number": "FH-110",
                "origin": "Islamabad",
                "destination": "Dubai",
                "departure_time": datetime(2025, 7, 15, 13, 45),
                "duration_minutes": 240,
                "price": 350.0,
                "total_seats": 85,
            },
            {
                "flight_number": "FH-111",
                "origin": "Lahore",
                "destination": "Karachi",
                "departure_time": datetime(2025, 7, 20, 19, 0),
                "duration_minutes": 120,
                "price": 105.0,
                "total_seats": 70,
            },
            {
                "flight_number": "FH-112",
                "origin": "Karachi",
                "destination": "London",
                "departure_time": datetime(2025, 7, 25, 23, 30),
                "duration_minutes": 480,
                "price": 820.0,
                "total_seats": 115,
            },
        ]
        
        for data in flights_data:
            flight = Flight(
                flight_number=data["flight_number"],
                origin=data["origin"],
                destination=data["destination"],
                departure_time=data["departure_time"],
                duration_minutes=data["duration_minutes"],
                price=data["price"],
                total_seats=data["total_seats"],
                seats_available=data["total_seats"],
            )
            db.add(flight)
        
        db.commit()
        print("Seeded 12 flights successfully.")
    
    finally:
        db.close()


if __name__ == "__main__":
    seed_flights()
