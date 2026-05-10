const express = require('express');
const path = require('path');
const app = express();

const PORT = process.env.PORT || 3000;
const API_BASE = process.env.BACKEND_URL || 'http://127.0.0.1:8000';

// Disable caching for static files
app.use((req, res, next) => {
  res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate, max-age=0');
  res.setHeader('Pragma', 'no-cache');
  res.setHeader('Expires', '0');
  next();
});

// Middleware
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

// Serve static HTML files
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

app.get('/search', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'search.html'));
});

app.get('/book/:flightId', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'book.html'));
});

app.get('/bookings', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'bookings.html'));
});

// Proxy API endpoints to FastAPI backend
app.get('/api/flights', async (req, res) => {
  try {
    const response = await fetch(`${API_BASE}/flights`);
    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json(data);
    }
    res.json(data);
  } catch (error) {
    console.error('Error fetching flights:', error);
    res.status(500).json({ error: 'Failed to fetch flights' });
  }
});

app.get('/api/flights/search', async (req, res) => {
  try {
    const params = new URLSearchParams();
    if (req.query.origin) params.append('origin', req.query.origin);
    if (req.query.destination) params.append('destination', req.query.destination);
    if (req.query.date) params.append('date', req.query.date);

    const response = await fetch(`${API_BASE}/flights/search?${params}`);
    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json(data);
    }
    res.json(data);
  } catch (error) {
    console.error('Error searching flights:', error);
    res.status(500).json({ error: 'Failed to search flights' });
  }
});

app.post('/api/bookings', async (req, res) => {
  try {
    const response = await fetch(`${API_BASE}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(req.body),
    });
    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json(data);
    }
    res.status(201).json(data);
  } catch (error) {
    console.error('Error creating booking:', error);
    res.status(500).json({ error: 'Failed to create booking' });
  }
});

app.get('/api/bookings', async (req, res) => {
  try {
    const params = new URLSearchParams();
    if (req.query.name) params.append('name', req.query.name);
    if (req.query.ref) params.append('ref', req.query.ref);

    const response = await fetch(`${API_BASE}/bookings?${params}`);
    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json(data);
    }
    res.json(data);
  } catch (error) {
    console.error('Error fetching bookings:', error);
    res.status(500).json({ error: 'Failed to fetch bookings' });
  }
});

app.delete('/api/bookings/:reference', async (req, res) => {
  try {
    const response = await fetch(`${API_BASE}/bookings/${req.params.reference}`, {
      method: 'DELETE',
    });
    const data = await response.json();
    if (!response.ok) {
      return res.status(response.status).json(data);
    }
    res.json(data);
  } catch (error) {
    console.error('Error cancelling booking:', error);
    res.status(500).json({ error: 'Failed to cancel booking' });
  }
});

app.listen(PORT, () => {
  console.log(`FlightHub frontend running on http://localhost:${PORT}`);
});
