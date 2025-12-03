# Potluck Organizer - Developer Documentation

This document contains technical information for developers working on the Potluck Organizer application.

## Architecture Overview

### Technology Stack

- **Backend**: FastAPI 0.115.0+
- **Server**: Uvicorn with websockets support
- **Database**: SQLite with SQLAlchemy 2.0+ ORM
- **Templates**: Jinja2
- **Validation**: Pydantic 2.10+ schemas
- **Authentication**: Session-based with bcrypt
- **CSS**: Pico CSS 2.0 (classless framework)
- **Icons**: Lucide icons
- **Package Manager**: uv (modern Python package installer)

### Project Structure

```
potluck/
├── app/
│   ├── main.py                 # FastAPI app, middleware, startup
│   ├── config.py               # Settings (pydantic-settings)
│   ├── database.py             # SQLAlchemy setup & sessions
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── crud.py                 # Business logic & DB operations
│   ├── routes/
│   │   ├── admin.py            # Admin routes (protected)
│   │   └── potluck.py          # Public attendee routes
│   ├── static/
│   │   ├── css/style.css       # Custom styles
│   │   └── js/main.js          # JavaScript utilities
│   └── templates/              # Jinja2 templates
│       ├── base.html           # Base layout
│       ├── index.html          # Landing/login page
│       ├── admin/              # Admin templates
│       │   ├── dashboard.html
│       │   ├── create.html
│       │   └── edit.html
│       └── potluck/            # Public templates
│           └── view.html
├── Dockerfile                  # Debian Trixie Slim base
├── docker-compose.yml          # Container orchestration
├── entrypoint.sh               # Container initialization
├── start.sh                    # Docker startup script
├── pyproject.toml              # Dependencies & project config
├── run.py                      # Development server
├── .env.example                # Environment template
└── potluck.db                  # SQLite database (created on first run)
```

## Database Schema

### Models

All models defined in `app/models.py`:

#### Potluck
```python
id: Integer (PK)
name: String(200)
description: Text (nullable)
url_slug: String(100) (unique, indexed)
created_at: DateTime
updated_at: DateTime

relationships:
  - categories: List[Category] (cascade delete)
```

#### Category
```python
id: Integer (PK)
potluck_id: Integer (FK -> Potluck)
name: String(200)
description: Text (nullable)
display_order: Integer (default: 0)

relationships:
  - potluck: Potluck
  - items: List[Item] (cascade delete)
```

#### Item
```python
id: Integer (PK)
category_id: Integer (FK -> Category)
name: String(200)
description: Text (nullable)
claim_limit: Integer (default: 1)
created_by_admin: Boolean (default: True)
require_details: Boolean (default: False)
created_at: DateTime

relationships:
  - category: Category
  - claims: List[Claim] (cascade delete)
```

#### Claim
```python
id: Integer (PK)
item_id: Integer (FK -> Item)
attendee_name: String(200)
item_details: Text (nullable)
session_id: String(255) (nullable)
claimed_at: DateTime

relationships:
  - item: Item
```

### Cascade Behavior

- Deleting a Potluck → deletes all Categories, Items, and Claims
- Deleting a Category → deletes all Items and Claims
- Deleting an Item → deletes all Claims

## API Routes

### Admin Routes (`app/routes/admin.py`)

All admin routes require authentication via `require_admin()` dependency.

```
POST   /admin/login                                    # Login with admin password
GET    /admin/logout                                   # Clear session
GET    /admin/dashboard                                # List all potlucks + stats
GET    /admin/create                                   # Create potluck form
POST   /admin/create                                   # Create potluck
GET    /admin/edit/{url_slug}                          # Edit potluck page
POST   /admin/edit/{url_slug}                          # Update potluck details
POST   /admin/edit/{url_slug}/add-category             # Add category
POST   /admin/edit/{url_slug}/category/{id}/update     # Update category
POST   /admin/edit/{url_slug}/category/{id}/delete     # Delete category
POST   /admin/edit/{url_slug}/category/{id}/add-item   # Add item to category
POST   /admin/edit/{url_slug}/item/{id}/update         # Update item
POST   /admin/edit/{url_slug}/item/{id}/delete         # Delete item
POST   /admin/edit/{url_slug}/claim/{id}/update        # Update claim
POST   /admin/edit/{url_slug}/claim/{id}/delete        # Delete claim
POST   /admin/delete/{url_slug}                        # Delete potluck
```

### Public Routes (`app/routes/potluck.py`)

```
GET    /p/{url_slug}                          # View potluck (public)
POST   /p/{url_slug}/claim/{item_id}          # Claim an item
POST   /p/{url_slug}/claim/{claim_id}/delete  # Remove own claim
```

### Root Routes (`app/main.py`)

```
GET    /                  # Landing page / Admin login
GET    /health            # Health check endpoint
```

## Business Logic (`app/crud.py`)

### Key Functions

- `generate_url_slug()` - Creates unique 8-character URL slugs using `secrets.token_urlsafe()`
- `can_claim_item(item, db)` - Checks if item has available claim slots
- `get_potluck_by_slug(url_slug, db)` - Retrieves potluck or raises 404
- Full CRUD operations for: Potluck, Category, Item, Claim

### Validation Logic

- **Claim Capacity**: `len(item.claims) < item.claim_limit`
- **Session Tracking**: Claims store `session_id` from cookie
- **Attendee Ownership**: Claims can only be deleted by matching session ID + attendee name

## Configuration

### Environment Variables (`.env`)

```bash
# Required
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_here

# Optional
DATABASE_URL=sqlite:///./potluck.db
DEBUG=False
```

### Configuration Management (`app/config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    admin_password: str
    secret_key: str
    database_url: str = "sqlite:///./potluck.db"
    debug: bool = False

    class Config:
        env_file = ".env"
        case_sensitive = False
```

Access settings via: `from app.config import get_settings`

## Development Setup

### Option 1: Local Development

1. **Install uv** (Python package manager):
   ```bash
   # See https://github.com/astral-sh/uv
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Create virtual environment and install dependencies**:
   ```bash
   uv venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   uv pip install -e .
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

4. **Run development server**:
   ```bash
   python run.py
   # or
   uvicorn app.main:app --reload --port 8000
   ```

### Option 2: Docker Development

1. **Build and run**:
   ```bash
   docker-compose up -d --build
   ```

2. **View logs**:
   ```bash
   docker-compose logs -f potluck
   ```

3. **Rebuild after code changes**:
   ```bash
   docker-compose up -d --build
   ```

### Database Initialization

The database is automatically created on startup via `app/main.py`:

```python
@app.on_event("startup")
async def startup_event():
    init_db()  # Creates all tables
```

Tables are created using SQLAlchemy's `Base.metadata.create_all(engine)`.

## Docker Details

### Dockerfile

- **Base Image**: `debian:trixie-slim`
- **Size**: ~200MB
- **Python**: System Python 3.x from Debian repos
- **Package Manager**: uv (installed from official script)
- **Dependencies**: Installed via `uv pip install`
- **Port**: 8000 (exposed)
- **Entrypoint**: `entrypoint.sh`

### docker-compose.yml

```yaml
services:
  potluck:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./.env:/app/.env
      - ./potluck.db:/app/potluck.db
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Volume Mounts

- `.env` - Environment configuration
- `potluck.db` - SQLite database (data persistence)

### Scripts

- `start.sh` - Creates `.env` and database file, runs `docker-compose up -d`
- `entrypoint.sh` - Container initialization (runs inside container)

## Security

### Current Implementation

1. **Password Authentication**: Session-based admin login
2. **Session Management**:
   - `SessionMiddleware` with 24-hour expiration
   - `SECRET_KEY` for session signing
   - CSRF protection via session middleware
3. **Input Validation**: Pydantic schemas validate all inputs
4. **SQL Injection Prevention**: SQLAlchemy ORM (parameterized queries)
5. **URL Slug Generation**: Cryptographically secure via `secrets.token_urlsafe(6)`
6. **Session-Based Claim Tracking**: Attendees identified by browser session

### Security Recommendations

- Use strong `ADMIN_PASSWORD` in production
- Generate cryptographically secure `SECRET_KEY` (32+ bytes hex)
- Set `DEBUG=False` in production
- Consider rate limiting for login endpoint
- Use HTTPS in production (reverse proxy with Nginx/Traefik)
- Consider PostgreSQL for better concurrency (SQLite limitations)
- Regular backups of `potluck.db`

## Frontend

### CSS Framework

**Pico CSS 2.0** (classless framework)
- Dark theme: `data-theme="dark"` on `<html>`
- Mobile-first responsive design
- No CSS classes needed for basic elements
- Custom overrides in `app/static/css/style.css`

### Custom Styling (`app/static/css/style.css`)

- Progress bars with color coding:
  - Green: 0-70% capacity
  - Warning: 71-90% capacity
  - Red: 91-100% capacity
- Card-based layouts
- Responsive tables → cards on mobile
- Custom button styles
- Form styling

### JavaScript (`app/static/js/main.js`)

- Click-to-copy for shareable links
- Lucide icon initialization
- Minimal client-side logic (server-side rendering preferred)

### Templates

**Jinja2 templates** with server-side rendering:
- `base.html` - Base layout with navigation
- `index.html` - Landing/login page
- `admin/dashboard.html` - Potluck list
- `admin/create.html` - Create potluck form
- `admin/edit.html` - Edit potluck (all CRUD operations)
- `potluck/view.html` - Public potluck view

## Testing

Currently no automated tests. Consider adding:
- Unit tests for CRUD operations (`pytest`)
- Integration tests for routes (`httpx` with FastAPI TestClient)
- E2E tests for user flows (`playwright`)

## Dependencies

Key dependencies from `pyproject.toml`:

```toml
[project.dependencies]
fastapi = ">=0.115.0"
uvicorn = {extras = ["standard"], version = "*"}
jinja2 = "*"
sqlalchemy = ">=2.0"
pydantic = ">=2.10"
pydantic-settings = "*"
python-multipart = "*"
bcrypt = "*"
itsdangerous = "*"
```

Install with:
```bash
uv pip install -e .
```

## Production Deployment Checklist

- [ ] Set secure `ADMIN_PASSWORD` (long, random)
- [ ] Generate new `SECRET_KEY` (32+ bytes)
- [ ] Set `DEBUG=False`
- [ ] Use PostgreSQL instead of SQLite (optional but recommended)
- [ ] Enable HTTPS (Nginx/Traefik reverse proxy)
- [ ] Set up regular database backups
- [ ] Configure firewall rules
- [ ] Use Gunicorn/Uvicorn workers for concurrency
- [ ] Set up monitoring (logs, health checks)
- [ ] Consider rate limiting
- [ ] Review and update dependencies regularly

## Common Development Tasks

### Add a new route

1. Define Pydantic schema in `app/schemas.py`
2. Add CRUD function in `app/crud.py`
3. Create route handler in `app/routes/admin.py` or `app/routes/potluck.py`
4. Create template in `app/templates/`
5. Update navigation in `app/templates/base.html` if needed

### Modify database schema

1. Update model in `app/models.py`
2. Delete `potluck.db` (dev only!)
3. Restart app to recreate tables

For production, use Alembic for migrations.

### Add new validation

1. Update schema in `app/schemas.py`
2. FastAPI automatically validates via Pydantic
3. Add custom validation in CRUD function if needed

### Debug issues

1. Enable debug mode: `DEBUG=True` in `.env`
2. Check logs: `docker-compose logs -f` or console output
3. Use FastAPI's automatic docs: http://localhost:8000/docs
4. Inspect database: `sqlite3 potluck.db`

## Extending the Application

### Ideas for Enhancement

- Email notifications when items are claimed
- Export potluck data (CSV, PDF)
- Multiple admin accounts
- Potluck templates/duplication
- Item categories (dietary restrictions, allergens)
- Attendee RSVP system
- Comments/notes per potluck
- File uploads (images of dishes)
- Calendar integration (iCal export)
- Multi-language support

### Migration to PostgreSQL

1. Update `DATABASE_URL` in `.env`:
   ```bash
   DATABASE_URL=postgresql://user:pass@localhost/potluck
   ```

2. Add PostgreSQL driver:
   ```bash
   uv pip install psycopg2-binary
   ```

3. Update `docker-compose.yml` to include PostgreSQL service
4. SQLAlchemy models remain the same (database-agnostic)

## Performance Considerations

- SQLite is suitable for small-medium deployments (<100 concurrent users)
- For larger deployments, migrate to PostgreSQL
- Consider caching for frequently accessed potlucks
- Add database indexes for common queries
- Use Gunicorn/Uvicorn workers for parallelism
- Enable gzip compression for responses
- CDN for static assets in production

## License

MIT License - See LICENSE file for details.
