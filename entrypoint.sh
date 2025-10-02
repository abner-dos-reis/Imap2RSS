#!/bin/bash

# Load environment variables from .env file if it exists
if [ -f /app/.env ]; then
    echo "Loading environment variables from .env file..."
    set -a  # automatically export all variables
    source /app/.env
    set +a  # turn off automatic export
fi

# Start the configuration GUI in the background
echo "Starting Configuration GUI..."
python config_gui.py &

# Start the IMAP converter in the background
echo "Starting IMAP to RSS converter..."
python app.py &

# Wait a moment for the converter to initialize
sleep 5

# Start the HTTP server in the foreground
echo "Starting RSS HTTP server..."
python server.py