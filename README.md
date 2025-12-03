# Potluck Organizer

A web application for organizing potlucks with shareable links. Admins create events with categories and items, attendees claim what they'll bring.

## Quick Start

**Prerequisites:** Docker and Docker Compose

```bash
./start.sh
```

That's it! The app runs at http://localhost:8000

The script will:
- Create `.env` from `.env.example` if needed
- Initialize the database
- Start the application

**First Time Setup:**
1. Edit `.env` to set a secure `ADMIN_PASSWORD`
2. Generate a `SECRET_KEY`:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
3. Update `SECRET_KEY` in `.env`

## Usage

### Admin
1. Visit http://localhost:8000 and login
2. Create a potluck with categories
3. Share the generated link with attendees

### Attendees
1. Visit the shareable link (e.g., http://localhost:8000/p/abc123xy)
2. Browse items and claim what you'll bring

## Management

```bash
# Stop
docker-compose down

# View logs
docker-compose logs -f

# Rebuild after changes
docker-compose up -d --build
```

## Data Persistence

Your database is stored in `potluck.db` and persists across container restarts. Back it up regularly.

## Tech Stack

FastAPI • SQLite • Jinja2 • Pico CSS

## Developer Information

See [CLAUDE.md](CLAUDE.md) for architecture, API documentation, and development setup.
