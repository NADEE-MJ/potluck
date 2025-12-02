"""Admin routes for potluck management."""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app import crud
from app.schemas import CategoryCreate, ItemCreate, CategoryUpdate, ItemUpdate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def require_admin(request: Request):
    """Dependency to check if user is admin."""
    if not request.session.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")


# Admin Login/Logout
@router.post("/login")
async def admin_login(request: Request, password: str = Form(...)):
    """Verify admin password and set session."""
    # Simple password comparison (consider using bcrypt hash in production)
    if password == settings.admin_password:
        # Password matches
        request.session["is_admin"] = True
        return RedirectResponse(url="/admin/dashboard", status_code=303)
    else:
        # Invalid password
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "error": "Invalid admin password"},
        )


@router.get("/logout")
async def admin_logout(request: Request):
    """Clear admin session."""
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


# Dashboard
@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Show admin dashboard with all potlucks."""
    potlucks = crud.get_all_potlucks(db)

    # Calculate stats for each potluck
    potlucks_data = []
    for potluck in potlucks:
        total_categories = len(potluck.categories)
        total_items = sum(len(cat.items) for cat in potluck.categories)
        total_claims = sum(
            len(item.claims) for cat in potluck.categories for item in cat.items
        )

        potlucks_data.append({
            "potluck": potluck,
            "total_categories": total_categories,
            "total_items": total_items,
            "total_claims": total_claims,
        })

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "potlucks_data": potlucks_data, "is_admin": True},
    )


# Create Potluck
@router.get("/create", response_class=HTMLResponse)
async def show_create_potluck(
    request: Request, _: None = Depends(require_admin)
):
    """Show create potluck form."""
    return templates.TemplateResponse(
        "admin/create_potluck.html",
        {"request": request, "is_admin": True},
    )


@router.post("/create")
async def create_potluck(
    request: Request,
    potluck_name: str = Form(...),
    potluck_description: str = Form(""),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Create a new potluck."""
    from app.schemas import PotluckCreate

    # Create potluck
    potluck_data = PotluckCreate(name=potluck_name, description=potluck_description)
    potluck = crud.create_potluck(db, potluck_data)

    # Redirect to edit page to add categories
    return RedirectResponse(
        url=f"/admin/edit/{potluck.url_slug}", status_code=303
    )


# Edit Potluck
@router.get("/edit/{url_slug}", response_class=HTMLResponse)
async def show_edit_potluck(
    url_slug: str,
    request: Request,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Show edit potluck page."""
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    return templates.TemplateResponse(
        "admin/edit_potluck.html",
        {"request": request, "potluck": potluck, "is_admin": True},
    )


# Update Potluck Info
@router.post("/edit/{url_slug}")
async def update_potluck(
    url_slug: str,
    request: Request,
    potluck_name: str = Form(...),
    potluck_description: str = Form(""),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Update potluck details."""
    from app.schemas import PotluckUpdate

    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    potluck_data = PotluckUpdate(name=potluck_name, description=potluck_description)
    crud.update_potluck(db, potluck, potluck_data)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


# Category Management
@router.post("/edit/{url_slug}/add-category")
async def add_category(
    url_slug: str,
    category_name: str = Form(...),
    category_description: str = Form(""),
    max_items: int = Form(10),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Add a category to a potluck."""
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    category_data = CategoryCreate(
        name=category_name, description=category_description, max_items=max_items
    )
    crud.create_category(db, potluck, category_data)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


@router.post("/edit/{url_slug}/category/{category_id}/update")
async def update_category(
    url_slug: str,
    category_id: int,
    category_name: str = Form(...),
    category_description: str = Form(""),
    max_items: int = Form(...),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Update a category."""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    category_data = CategoryUpdate(
        name=category_name, description=category_description, max_items=max_items
    )
    crud.update_category(db, category, category_data)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


@router.post("/edit/{url_slug}/category/{category_id}/delete")
async def delete_category(
    url_slug: str,
    category_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Delete a category."""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    crud.delete_category(db, category)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


# Item Management
@router.post("/edit/{url_slug}/category/{category_id}/add-item")
async def add_item(
    url_slug: str,
    category_id: int,
    item_name: str = Form(...),
    item_description: str = Form(""),
    claim_limit: int = Form(1),
    require_details: bool = Form(False),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Add an item to a category."""
    category = crud.get_category(db, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    item_data = ItemCreate(
        name=item_name,
        description=item_description,
        claim_limit=claim_limit,
        require_details=require_details,
    )
    crud.create_item(db, category, item_data, created_by_admin=True)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


@router.post("/edit/{url_slug}/item/{item_id}/update")
async def update_item(
    url_slug: str,
    item_id: int,
    item_name: str = Form(...),
    item_description: str = Form(""),
    claim_limit: int = Form(...),
    require_details: bool = Form(False),
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Update an item."""
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    item_data = ItemUpdate(
        name=item_name,
        description=item_description,
        claim_limit=claim_limit,
        require_details=require_details,
    )
    crud.update_item(db, item, item_data)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


@router.post("/edit/{url_slug}/item/{item_id}/delete")
async def delete_item(
    url_slug: str,
    item_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Delete an item."""
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    crud.delete_item(db, item)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


# Claim Management (Admin can delete any claim)
@router.post("/edit/{url_slug}/claim/{claim_id}/delete")
async def delete_claim_admin(
    url_slug: str,
    claim_id: int,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Delete a claim (admin only)."""
    claim = crud.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    crud.delete_claim(db, claim)

    return RedirectResponse(url=f"/admin/edit/{url_slug}", status_code=303)


# Delete Potluck
@router.post("/delete/{url_slug}")
async def delete_potluck(
    url_slug: str,
    db: Session = Depends(get_db),
    _: None = Depends(require_admin),
):
    """Delete an entire potluck."""
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    crud.delete_potluck(db, potluck)

    return RedirectResponse(url="/", status_code=303)
