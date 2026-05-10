from datetime import datetime


def test_get_all_flights_empty(client):
    response = client.get("/flights")
    assert response.status_code == 200
    assert response.json() == []


def test_create_flight_success(client):
    payload = {
        "flight_number": "FH-777",
        "origin": "Karachi",
        "destination": "Dubai",
        "departure_time": datetime(2025, 6, 10, 12, 0, 0).isoformat(),
        "duration_minutes": 180,
        "price": 320.0,
        "total_seats": 50,
    }

    response = client.post("/flights", json=payload)

    assert response.status_code == 201
    body = response.json()
    assert body["flight_number"] == "FH-777"
    assert body["seats_available"] == body["total_seats"] == 50


def test_search_flights_by_origin(client, sample_flight):
    response = client.get("/flights/search", params={"origin": "Karachi"})

    assert response.status_code == 200
    body = response.json()
    assert len(body) >= 1
    assert body[0]["origin"] == "Karachi"
