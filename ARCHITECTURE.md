# FlightHub Architecture

## 1. Data Model

FlightHub uses a simple relational model with two core tables: `flights` and `bookings`.

### `flights`
Each row represents a single scheduled flight.

Fields:
- `id`: integer primary key
- `flight_number`: unique flight code such as `FH-101`
- `origin`: departure city or airport name
- `destination`: arrival city or airport name
- `departure_time`: timezone-aware datetime
- `duration_minutes`: integer flight duration
- `price`: ticket price as a floating-point value
- `total_seats`: total capacity of the flight
- `seats_available`: remaining bookable seats

Notes:
- `flight_number` is unique so each flight can be identified cleanly in APIs and the UI.
- `seats_available` is stored directly instead of being calculated every time, which makes booking and cancellation logic simpler.
- `departure_time` is stored with timezone support to avoid ambiguity in scheduling.

### `bookings`
Each row represents a passenger booking for a flight.

Fields:
- `id`: integer primary key
- `booking_reference`: unique human-readable booking reference such as `FH-ABC123`
- `flight_id`: foreign key to `flights.id`
- `passenger_name`: passenger full name
- `passport_number`: passport or travel document number
- `seat_number`: assigned seat label such as `12A`
- `status`: booking state, currently `confirmed` or `cancelled`
- `created_at`: booking creation timestamp in UTC

Relationships:
- One flight can have many bookings.
- One booking belongs to exactly one flight.
- Deleting a flight cascades to its bookings because the ORM relationship uses delete-orphan behavior.

### Business rules enforced by the model and routers
- A flight cannot have more bookings than its remaining seat count.
- Seat numbers are unique per flight for confirmed bookings.
- Cancelling a booking restores one seat back to the flight.
- Bookings are not hard deleted; they are soft-cancelled by status.

---

## 2. API Design

FlightHub exposes a REST API through FastAPI. The backend runs on port `8000`, and the frontend proxies requests through `/api`.

### Application setup
- `GET /` returns a health check response.
- CORS allows requests from `http://localhost:3000`.
- Database tables are created on application startup.

### Flight endpoints

#### `GET /flights`
Returns all flights currently stored in the database.

Response:
- `200 OK`
- JSON array of flight objects

#### `POST /flights`
Creates a new flight.

Validation and behavior:
- `flight_number` must be unique.
- `seats_available` is initialized from `total_seats`.
- Returns the created flight record.

Response:
- `201 Created`
- `409 Conflict` if the flight number already exists

#### `GET /flights/search`
Searches flights by optional filters.

Query parameters:
- `origin`
- `destination`
- `date`

Behavior:
- At least one filter is required.
- `origin` and `destination` use case-insensitive matching.
- `date` matches the beginning of the departure timestamp string.

Response:
- `200 OK` with matching flights
- `400 Bad Request` if no search parameter is provided
- `404 Not Found` if no flights match

### Booking endpoints

#### `POST /bookings`
Creates a booking for a flight.

Validation and behavior:
- Flight must exist.
- The flight must have available seats.
- The requested seat number must not already be taken on that flight by another confirmed booking.
- A booking reference is generated automatically.
- `seats_available` is reduced by one after a successful booking.

Response:
- `201 Created`
- `404 Not Found` if the flight does not exist
- `409 Conflict` if the flight is full or the seat is already taken

#### `GET /bookings`
Searches bookings by passenger name or booking reference.

Query parameters:
- `name`
- `ref`

Behavior:
- At least one filter is required.
- `ref` has priority over `name` if both are supplied.
- `name` uses case-insensitive partial matching.

Response:
- `200 OK` with matching bookings
- `400 Bad Request` if no search parameter is provided
- `404 Not Found` if nothing matches

#### `DELETE /bookings/{reference}`
Cancels a booking by booking reference.

Behavior:
- Booking must exist.
- A booking that is already cancelled cannot be cancelled again.
- The booking status is changed to `cancelled`.
- One seat is returned to the flight.

Response:
- `200 OK`
- `404 Not Found` if the booking does not exist
- `400 Bad Request` if the booking is already cancelled

### API response strategy
- Successful write operations return the created or updated object.
- Errors return structured FastAPI `detail` messages.
- The frontend depends on these status codes to show the correct error or success state.

---

## 3. How Ambiguities Were Resolved

Several design choices were not fully specified, so the implementation uses consistent rules that keep the system simple and predictable.

### 1. Seat inventory handling
Ambiguity: should seats be computed from bookings or stored directly?

Resolution:
- `seats_available` is stored on the flight row.
- It is decremented when a booking is created and incremented when a booking is cancelled.

Reason:
- This keeps booking logic fast and easy to display in the UI.
- It avoids recalculating availability on every request.

### 2. Cancel vs delete
Ambiguity: should a booking be removed from the database when cancelled?

Resolution:
- Bookings are not deleted.
- The system sets `status = cancelled`.

Reason:
- This preserves booking history and makes auditing easier.
- The frontend can still show the booking record and its status.

### 3. Seat uniqueness scope
Ambiguity: should a seat number be unique globally or only within a flight?

Resolution:
- Seat uniqueness is enforced only within the same flight for confirmed bookings.

Reason:
- Seat labels like `12A` are reused across different flights.
- The actual conflict only matters for passengers on the same flight.

### 4. Search matching rules
Ambiguity: should search use exact match, partial match, or prefix match?

Resolution:
- `origin` and `destination` use case-insensitive matching.
- Booking name search uses case-insensitive partial matching.
- Date search uses a prefix match on the stored timestamp.

Reason:
- This makes the UI forgiving for real user input.
- The date filter is easy to use from a date picker or string input.

### 5. Booking reference format
Ambiguity: what format should the booking reference use?

Resolution:
- References use the pattern `FH-XXXXXX` generated from a UUID fragment.

Reason:
- The value is short, readable, and low risk for collisions.
- It is suitable for user-facing lookup and cancellation.

### 6. Time handling
Ambiguity: should times be local or timezone-aware?

Resolution:
- Departure and creation times are stored as timezone-aware datetimes.
- Creation timestamps use UTC.

Reason:
- This avoids inconsistent time interpretation across browsers and servers.

---

## Summary

FlightHub is built around a minimal but complete booking model:
- one `Flight` entity for schedule and capacity
- one `Booking` entity for passenger reservations
- REST endpoints for listing, searching, booking, and cancelling

The main architectural goal is clarity over complexity. The backend keeps state explicit, the API returns predictable status codes, and the frontend can render and update the booking experience without additional business logic.
