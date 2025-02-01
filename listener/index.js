const express = require('express');
const bodyParser = require('body-parser');

const app = express();
const PORT = 8080;

// Middleware to parse JSON payloads
app.use(bodyParser.json());

// Endpoint to handle the callback
app.post('/listen', (req, res) => {
    try {
        const data = req.body;

        // Log the received callback data
        console.log('Callback received:', data);

        // Respond to the sender
        res.status(200).json({
            status: 'success',
            message: 'Callback processed successfully',
        });
    } catch (error) {
        console.error('Error processing callback:', error);
        res.status(500).json({
            status: 'error',
            message: 'Internal server error',
        });
    }
});

app.get('/listen', (req, res) => {
    try {
        const data = req.body;

        // Log the received callback data
        console.log('Callback received:', data);

        // Respond to the sender
        res.status(200).json({
            status: 'success',
            message: 'Callback processed successfully',
        });
    } catch (error) {
        console.error('Error processing callback:', error);
        res.status(500).json({
            status: 'error',
            message: 'Internal server error',
        });
    }
});

// Start the server
app.listen(PORT, '0.0.0.0', () => {
    console.log(`Callback server is running on http://0.0.0.0:${PORT}/listen`);
});
