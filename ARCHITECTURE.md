# ARCHITECTURE.md - FlightHub

## Table of Contents
1. [System Overview](#1-system-overview)
2. [Technology Stack](#2-technology-stack)
3. [Folder Structure](#3-folder-structure)
4. [Data Model](#4-data-model)
5. [API Design](#5-api-design)
6. [Ambiguity Resolutions](#6-ambiguity-resolutions)
7. [Key Design Decisions](#7-key-design-decisions)

---

## 1. System Overview

FlightHub runs as two processes:

- FastAPI backend on port `8000` for business logic and database operations.
- Express frontend server on port `3000` for serving static pages and proxying browser API calls to the backend.

```text
Browser (HTML + Vanilla JS)
        |
        | fetch('/api/...')
        v
Express Frontend (:3000)
  - serves static files
  - proxies /api/* to FastAPI
        |
        v
FastAPI Backend (:8000)
  - validation + booking rules + persistence
        |
        v
SQLite (flighthub.db)
```

CORS is enabled on FastAPI for `http://localhost:3000`.

---

## 2. Technology Stack

| Layer | Technology | Why Used |
|------|------------|----------|
| Backend API | FastAPI (Python 3.11) | Fast REST implementation with validation support |
| ORM | SQLAlchemy 2.x | ORM models and database session management |
| Validation | Pydantic v2 | Request/response schemas and field validation |
| Database | SQLite | Simple file-based persistence for this project scope |
| Backend Server | Uvicorn | ASGI server for FastAPI |
| Frontend Server | Express (Node.js) | Static hosting and API proxy |
| UI | HTML + CSS + Vanilla JavaScript | Lightweight client without frontend framework |
| Tests | Pytest + FastAPI TestClient + HTTPX | Endpoint tests with in-memory SQLite |

---

## 3. Folder Structure

```text
savvpro-test-flight/
|
|-- backend/
|   |-- main.py               # FastAPI app, CORS, router wiring
|   |-- database.py           # engine, SessionLocal, get_db
|   |-- models.py             # Flight and Booking SQLAlchemy models
|   |-- schemas.py            # Pydantic request/response schemas
|   |-- seed.py               # Seeds 12 sample flights
|   \-- routers/
|       |-- flights.py        # /flights and /flights/search
|       \-- bookings.py       # /bookings and cancel endpoint
|
|-- frontend/
|   |-- server.js             # Express server + /api proxy routes
|   |-- package.json
|   \-- public/
|       |-- index.html
|       |-- search.html
|       |-- book.html
|       |-- bookings.html
|       \-- styles.css
|
|-- tests/
|   |-- conftest.py           # in-memory DB and TestClient fixtures
|   |-- test_flights.py       # flight endpoint tests
|   \-- test_bookings.py      # booking endpoint tests (business rule included)
|
|-- README.md
|-- ARCHITECTURE.md
|-- AIUsage.md
|-- userGuide.md
|-- requirements.txt
|-- pyproject.toml
|-- pytest.ini
\-- TASK.md
```

---

## 4. Data Model

### Table: flights

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, autoincrement | Internal flight ID |
| flight_number | TEXT | NOT NULL, UNIQUE | e.g., FH-101 |
| origin | TEXT | NOT NULL | Departure city |
| destination | TEXT | NOT NULL | Arrival city |
| departure_time | DATETIME | NOT NULL | Departure date-time |
| duration_minutes | INTEGER | NOT NULL | Duration in minutes |
| price | REAL | NOT NULL | Price per seat |
| total_seats | INTEGER | NOT NULL | Total capacity |
| seats_available | INTEGER | NOT NULL | Remaining seats |

### Table: bookings

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PK, autoincrement | Internal booking ID |
| booking_reference | TEXT | NOT NULL, UNIQUE | e.g., FH-A1B2C3 |
| flight_id | INTEGER | FK -> flights.id | Linked flight |
| passenger_name | TEXT | NOT NULL | Passenger full name |
| passport_number | TEXT | NOT NULL | Passport identifier |
| seat_number | TEXT | NOT NULL | Requested seat (e.g., 12A) |
| status | TEXT | NOT NULL | confirmed or cancelled |
| created_at | DATETIME | NOT NULL | Booking creation timestamp |

### Relationship

```text
flights (1) ------ (many) bookings
```

Operational behavior:

- `seats_available` decreases on booking confirmation.
- `seats_available` increases on booking cancellation.
- Booking records are soft-cancelled using `status = "cancelled"`.

---

## 5. API Design

All endpoints return JSON.

### Health

#### GET /
Returns service status.

Example response:

```json
{
  "status": "ok",
  "message": "FlightHub API is running"
}
```

### Flights

#### GET /flights
Returns all flights.

- `200 OK`: list of flight objects.

#### POST /flights
Creates a flight.

Behavior:

- Rejects duplicate `flight_number`.
- Sets `seats_available = total_seats`.

Responses:

- `201 Created`
- `409 Conflict` with `Flight number <code> already exists.`

#### GET /flights/search
Searches flights by optional parameters: `origin`, `destination`, `date`.

Behavior:

- If all parameters are missing: `400 Bad Request`.
- `origin` and `destination` use case-insensitive matching.
- `date` matches timestamp prefix (`YYYY-MM-DD`).

Responses:

- `200 OK` with matching flights
- `400 Bad Request`: `Provide at least one search parameter: origin, destination, date.`
- `404 Not Found`: `No flights found matching the given criteria.`

### Bookings

#### POST /bookings
Creates a booking.

Request fields:

- `flight_id`
- `passenger_name`
- `passport_number`
- `seat_number`

Behavior:

- Flight must exist.
- Flight must have seats available.
- Same seat cannot be reused for confirmed bookings on the same flight.
- Generates reference format `FH-XXXXXX`.
- Reduces `seats_available` by one.

Responses:

- `201 Created`
- `404 Not Found`: `Flight not found.`
- `409 Conflict`: full flight or seat already taken

#### GET /bookings
Searches bookings using `name` or `ref`.

Behavior:

- Requires at least one of `name` or `ref`.
- `ref` takes precedence if both are provided.
- `name` uses case-insensitive partial match.

Responses:

- `200 OK` with booking list
- `400 Bad Request`: `Provide at least one search parameter: name or ref.`
- `404 Not Found`: `No bookings found.`

#### DELETE /bookings/{reference}
Cancels a booking and restores seat availability.

Behavior:

- Booking must exist.
- Already-cancelled booking cannot be cancelled again.
- Sets `status` to `cancelled`.
- Adds one seat back to the flight.

Responses:

- `200 OK` with:

```json
{
  "booking_reference": "FH-XXXXXX",
  "status": "cancelled",
  "message": "Booking FH-XXXXXX has been successfully cancelled."
}
```

- `404 Not Found`: `Booking <reference> not found.`
- `400 Bad Request`: `Booking <reference> is already cancelled.`

---

## 6. Ambiguity Resolutions

### Ambiguity 1: Handle overbooking appropriately

Decision:

- Overbooking is blocked.
- When `seats_available <= 0`, booking request is rejected with `409 Conflict`.

Why:

- Clear and deterministic behavior for staff and frontend.
- Matches a simple operational model for this project scope.

### Ambiguity 2: Display relevant flight information

Decision:

- Flight UI prioritizes: route, departure time, duration, price, and seats available.
- Booking page additionally emphasizes selected flight summary and passenger form.

Why:

- These fields are directly needed to decide and complete a booking.
- Keeps screens focused on booking workflow instead of secondary details.

---

## 7. Key Design Decisions

### 1. Express proxy pattern

The frontend does not call `:8000` directly from browser pages. Instead, browser code calls `/api/*` on Express, and Express forwards to FastAPI. This keeps frontend requests simple and avoids browser-side cross-origin complexity.

### 2. Soft cancellation

Cancellation updates booking status instead of deleting rows, preserving booking history.

### 3. Test approach

Tests run against an isolated in-memory SQLite database with dependency overrides.

Current test coverage includes:

- Flight list empty case
- Flight creation success
- Flight search by origin
- Booking creation with seat decrement (business rule)
- Booking cancellation with seat restoration (business rule)

(Validated: `5 passed`.)

### 4. Seed behavior

`backend/seed.py` inserts 12 realistic flights and exits early with `Database already seeded.` if data already exists.

---

Document version: 1.1
