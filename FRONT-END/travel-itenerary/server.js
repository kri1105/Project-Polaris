// server.js
require('dotenv').config();
const express = require('express');
const cors = require('cors');
const fetch = (...args) =>
    import('node-fetch').then(({default: fetch}) => fetch(...args));

const app = express();
const port = process.env.PORT || 3000;

const googleMapsApiKey = process.env.GOOGLE_MAPS_API_KEY;
const weatherApiKey = process.env.WEATHER_API_KEY;

const allowedOrigins = ['http://localhost', 'http://localhost:*']; // Replace with your production URL
app.use(cors({
    origin: function (origin, callback) {
        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error('Not allowed by CORS'));
        }
    }
}));

app.use(express.json());

app.get('/api/places', async (req, res) => {
    const { lat, lng, query } = req.query;

    if (!lat || !lng || !query) {
        return res.status(400).json({ error: "Missing required parameters (lat, lng, query)" });
    }

    const apiUrl = `https://maps.googleapis.com/maps/api/place/nearbysearch/json?location=${lat},${lng}&radius=5000&type=tourist_attraction&key=${googleMapsApiKey}&query=${query}`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Google Maps API Error: ${response.status} - ${response.statusText} - ${JSON.stringify(errorData)}`);
        }

        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error("Error in Google Maps API call:", error);
        res.status(500).json({ error: 'Failed to fetch places' });
    }
});

app.get('/api/weather', async (req, res) => {
    const { city } = req.query;

    if (!city) {
        return res.status(400).json({ error: "Missing required parameter (city)" });
    }

    const apiUrl = `https://api.weatherapi.com/v1/forecast.json?key=${weatherApiKey}&q=${city}&days=7`;

    try {
        const response = await fetch(apiUrl);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`Weather API Error: ${response.status} - ${response.statusText} - ${JSON.stringify(errorData)}`);
        }
        const data = await response.json();
        res.json(data);
    } catch (error) {
        console.error("Error in Weather API call:", error);
        res.status(500).json({ error: 'Failed to fetch weather data' });
    }
});

app.listen(port, () => {
    console.log(`Server listening on port ${port}`);
});