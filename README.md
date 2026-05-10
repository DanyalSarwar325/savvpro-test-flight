# FlightHub

FlightHub is a flight booking system with a FastAPI backend and an Express.js frontend.

## Assumptions

- You are running the project on Windows.
- Python, Node.js, and `uv` are installed and available in your terminal.
- The backend dependency file is located at the repository root as `requirements.txt`.
- The frontend uses an Express server on port `3000`.
- The backend uses FastAPI on port `8000`.

## Setup Instructions

### Backend

1. Open a terminal in the project root.
2. Create a virtual environment:

   ```bash
   uv venv
   ```

3. Activate the virtual environment.

   On PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

   On Command Prompt:

   ```cmd
   .venv\Scripts\activate
   ```

4. Move into the backend folder:

   ```bash
   cd backend
   ```

5. Install backend dependencies from the root requirements file:

   ```bash
   uv add -r ..\requirements.txt
   ```

6. Start the backend server:

   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

### Frontend

1. Open a new terminal in the project root.
2. Move into the frontend folder:

   ```bash
   cd frontend
   ```

3. Install frontend dependencies:

   ```bash
   npm install
   ```

4. Start the Express server:

   ```bash
   npm start
   ```

## How to Run the Project

1. Start the backend first on `http://127.0.0.1:8000`.
2. Start the frontend second on `http://localhost:3000`.
3. Open `http://localhost:3000` in your browser.
4. Use the Flights, Search, Book, and My Bookings pages from the UI.

## Notes

- The frontend proxies API requests to the backend.
- If the page styling or API responses look stale, hard refresh the browser.
- Seed data can be loaded separately if needed for testing.
