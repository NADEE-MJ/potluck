#!/bin/sh
set -e

# Create .env from .env.example if it doesn't exist
if [ ! -f /app/.env ]; then
    echo "Creating .env from .env.example..."
    cp /app/.env.example /app/.env
fi

# Create empty database file if it doesn't exist
if [ ! -f /app/potluck.db ]; then
    echo "Creating empty database file..."
    touch /app/potluck.db
fi

# Execute the main command
exec "$@"
