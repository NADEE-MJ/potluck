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

    # Get user's session ID (if they have one)
    user_session_id = request.session.get("user_session_id")

    # Get flash messages from session
    error_message = request.session.pop("error", None)
    success_message = request.session.pop("success", None)

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
            "user_session_id": user_session_id,
            "error_message": error_message,
            "success_message": success_message,
        },
    )


@router.post("/p/{url_slug}/claim/{item_id}")
async def claim_item(
    url_slug: str,
    item_id: int,
    request: Request,
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
        request.session["error"] = f"Sorry, '{item.name}' is already fully claimed ({item.claim_limit}/{item.claim_limit}). Please choose another item."
        return RedirectResponse(url=f"/p/{url_slug}", status_code=303)

    # Check if details are required but not provided
    if item.require_details and not item_details.strip():
        request.session["error"] = f"Please provide details about what you're bringing for '{item.name}'."
        return RedirectResponse(url=f"/p/{url_slug}", status_code=303)

    # Get or create session ID for this browser
    if "user_session_id" not in request.session:
        import secrets
        request.session["user_session_id"] = secrets.token_urlsafe(32)

    session_id = request.session["user_session_id"]

    # Create claim
    claim_data = ClaimCreate(attendee_name=attendee_name, item_details=item_details)
    crud.create_claim(db, item, claim_data, session_id=session_id)

    request.session["success"] = f"Successfully claimed '{item.name}'!"
    return RedirectResponse(url=f"/p/{url_slug}", status_code=303)


@router.post("/p/{url_slug}/claim/{claim_id}/delete")
async def delete_claim_public(
    url_slug: str,
    claim_id: int,
    request: Request,
    verify_name: str = Form(...),
    db: Session = Depends(get_db),
):
    """Remove a claim (public) - requires session verification."""
    # Verify potluck exists
    potluck = crud.get_potluck_by_slug(db, url_slug)
    if not potluck:
        raise HTTPException(status_code=404, detail="Potluck not found")

    # Get claim
    claim = crud.get_claim(db, claim_id)
    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    # Verify the session ID matches
    user_session_id = request.session.get("user_session_id")
    if not user_session_id or claim.session_id != user_session_id:
        request.session["error"] = "You can only remove your own claims."
        return RedirectResponse(url=f"/p/{url_slug}", status_code=303)

    # Additional name verification for extra security
    if claim.attendee_name.strip().lower() != verify_name.strip().lower():
        request.session["error"] = "Name doesn't match. Please enter the exact name you used when claiming."
        return RedirectResponse(url=f"/p/{url_slug}", status_code=303)

    # Delete claim
    crud.delete_claim(db, claim)

    request.session["success"] = "Claim removed successfully!"
    return RedirectResponse(url=f"/p/{url_slug}", status_code=303)
