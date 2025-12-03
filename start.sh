#!/bin/bash
# Initialize required files for docker-compose

# Create .env from template if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ .env created. Please edit it to set your ADMIN_PASSWORD and SECRET_KEY"
fi

# Create empty database file if it doesn't exist
if [ ! -f potluck.db ]; then
    echo "Creating empty database file..."
    touch potluck.db
    echo "✓ potluck.db created"
fi

echo "Starting docker-compose..."
docker-compose down
docker-compose build
docker-compose up
