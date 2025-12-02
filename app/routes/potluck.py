"""Public potluck routes for attendees."""
from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app import crud
from app.schemas import ClaimCreate, ItemCreate

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/p/{url_slug}", response_class=HTMLResponse)
async def view_potluck(
    url_slug: str,
    request: Request,
    db: Session = Depends(get_db),
):
    """View a potluck (public)."""
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    # Calculate statistics for each category and item
    categories_data = []
    for category in potluck.categories:
        items_data = []
        for item in category.items:
            claim_count = len(item.claims)
            items_data.append({
                "item": item,
                "claim_count": claim_count,
                "can_claim": claim_count < item.claim_limit,
                "claims": item.claims,
            })

        categories_data.append({
            "category": category,
            "item_count": len(category.items),
            "items_list": items_data,
        })

    return templates.TemplateResponse(
        "potluck/view.html",
        {
            "request": request,
            "potluck": potluck,
            "categories_data": categories_data,
            "url_slug": url_slug,
        },
    )


@router.post("/p/{url_slug}/claim/{item_id}")
async def claim_item(
    url_slug: str,
    item_id: int,
    attendee_name: str = Form(...),
    item_details: str = Form(""),
    db: Session = Depends(get_db),
):
    """Claim an item (public)."""
    # Verify potluck exists
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    # Get item
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if item can be claimed
    if not crud.can_claim_item(db, item_id):
        raise HTTPException(
            status_code=400,
            detail=f"Item is fully claimed ({item.claim_limit}/{item.claim_limit})",
        )

    # Check if details are required but not provided
    if item.require_details and not item_details.strip():
        raise HTTPException(
            status_code=400,
            detail="Please provide details about what you're bringing for this item",
        )

    # Create claim
    claim_data = ClaimCreate(attendee_name=attendee_name, item_details=item_details)
    crud.create_claim(db, item, claim_data)

    return RedirectResponse(url=f"/p/{url_slug}", status_code=303)


@router.post("/p/{url_slug}/claim/{claim_id}/delete")
async def delete_claim_public(
    url_slug: str,
    claim_id: int,
    verify_name: str = Form(...),
    db: Session = Depends(get_db),
):
    """Remove a claim (public) - requires name verification."""
    # Verify potluck exists
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    # Get claim
    claim = crud.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Verify the name matches (case-insensitive)
    if claim.attendee_name.strip().lower() != verify_name.strip().lower():
        raise HTTPException(
            status_code=403,
            detail="Name doesn't match. You can only remove your own claims."
        )

    # Delete claim
    crud.delete_claim(db, claim)

    return RedirectResponse(url=f"/p/{url_slug}", status_code=303)
