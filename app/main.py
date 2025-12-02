"""Main FastAPI application."""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.database import init_db
from app.routes import admin, potluck

# Create FastAPI app
app = FastAPI(
    title="Potluck Organizer",
    description="A web app for organizing potlucks with categories and items",
    version="1.0.0",
)

# Add session middleware for admin authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    max_age=3600 * 24,  # 24 hours
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="app/templates")

# Include routers
app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(potluck.router, tags=["potluck"])


# Startup event
@app.on_event("startup")
def on_startup():
    """Initialize database on startup."""
    init_db()
    print("Database initialized successfully!")


# Root route
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Landing page / Admin login."""
    is_admin = request.session.get("is_admin", False)
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "is_admin": is_admin},
    )


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
