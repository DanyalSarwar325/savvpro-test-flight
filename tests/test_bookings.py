def test_create_booking_decrements_seats_business_rule(client, sample_flight):
    booking_payload = {
        "flight_id": sample_flight.id,
        "passenger_name": "John Doe",
        "passport_number": "AB123456",
        "seat_number": "1A",
    }

    create_response = client.post("/bookings", json=booking_payload)

    assert create_response.status_code == 201
    booking_body = create_response.json()
    assert booking_body["status"] == "confirmed"
    assert booking_body["booking_reference"].startswith("FH-")

    flights_response = client.get("/flights")
    assert flights_response.status_code == 200
    flights = flights_response.json()
    assert len(flights) == 1
    assert flights[0]["seats_available"] == 1


def test_cancel_booking_restores_seat(client, sample_flight):
    create_response = client.post(
        "/bookings",
        json={
            "flight_id": sample_flight.id,
            "passenger_name": "Jane Doe",
            "passport_number": "XY987654",
            "seat_number": "2A",
        },
    )
    ref = create_response.json()["booking_reference"]

    cancel_response = client.delete(f"/bookings/{ref}")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    flights_response = client.get("/flights")
    assert flights_response.status_code == 200
    flights = flights_response.json()
    assert flights[0]["seats_available"] == 2
