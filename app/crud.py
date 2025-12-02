"""CRUD operations and business logic."""
import secrets
import string
from typing import Optional
from sqlalchemy.orm import Session
from app.models import Potluck, Category, Item, Claim
from app.schemas import (
    PotluckCreate,
    PotluckUpdate,
    CategoryCreate,
    CategoryUpdate,
    ItemCreate,
    ItemUpdate,
    ClaimCreate,
    ClaimUpdate,
)


# URL Slug Generation
def generate_url_slug(db: Session, length: int = 8) -> str:
    """Generate a unique URL slug for a potluck."""
    chars = string.ascii_lowercase + string.digits
    while True:
        slug = "".join(secrets.choice(chars) for _ in range(length))
        if not db.query(Potluck).filter(Potluck.url_slug == slug).first():
            return slug


# Potluck CRUD
def create_potluck(db: Session, potluck_data: PotluckCreate) -> Potluck:
    """Create a new potluck."""
    potluck = Potluck(
        name=potluck_data.name,
        description=potluck_data.description,
        url_slug=generate_url_slug(db),
    )
    db.add(potluck)
    db.commit()
    db.refresh(potluck)
    return potluck


def get_potluck_by_slug(db: Session, url_slug: str) -> Optional[Potluck]:
    """Get a potluck by its URL slug."""
    return db.query(Potluck).filter(Potluck.url_slug == url_slug).first()


def get_all_potlucks(db: Session):
    """Get all potlucks ordered by most recent first."""
    return db.query(Potluck).order_by(Potluck.created_at.desc()).all()


def update_potluck(db: Session, potluck: Potluck, potluck_data: PotluckUpdate) -> Potluck:
    """Update a potluck."""
    if potluck_data.name is not None:
        potluck.name = potluck_data.name
    if potluck_data.description is not None:
        potluck.description = potluck_data.description
    db.commit()
    db.refresh(potluck)
    return potluck


def delete_potluck(db: Session, potluck: Potluck) -> None:
    """Delete a potluck (cascades to categories, items, and claims)."""
    db.delete(potluck)
    db.commit()


# Category CRUD
def create_category(
    db: Session, potluck: Potluck, category_data: CategoryCreate
) -> Category:
    """Create a new category for a potluck."""
    category = Category(
        potluck_id=potluck.id,
        name=category_data.name,
        description=category_data.description,
        max_items=category_data.max_items,
        display_order=category_data.display_order,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Get a category by ID."""
    return db.query(Category).filter(Category.id == category_id).first()


def update_category(
    db: Session, category: Category, category_data: CategoryUpdate
) -> Category:
    """Update a category."""
    if category_data.name is not None:
        category.name = category_data.name
    if category_data.description is not None:
        category.description = category_data.description
    if category_data.max_items is not None:
        category.max_items = category_data.max_items
    if category_data.display_order is not None:
        category.display_order = category_data.display_order
    db.commit()
    db.refresh(category)
    return category


def delete_category(db: Session, category: Category) -> None:
    """Delete a category (cascades to items and claims)."""
    db.delete(category)
    db.commit()


def can_add_item_to_category(db: Session, category_id: int) -> bool:
    """Check if a category has space for more items."""
    category = get_category(db, category_id)
    if not category:
        return False

    current_item_count = db.query(Item).filter(Item.category_id == category_id).count()
    return current_item_count < category.max_items


# Item CRUD
def create_item(
    db: Session,
    category: Category,
    item_data: ItemCreate,
    created_by_admin: bool = True,
) -> Item:
    """Create a new item in a category."""
    item = Item(
        category_id=category.id,
        name=item_data.name,
        description=item_data.description,
        claim_limit=item_data.claim_limit,
        created_by_admin=created_by_admin,
        require_details=item_data.require_details,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def get_item(db: Session, item_id: int) -> Optional[Item]:
    """Get an item by ID."""
    return db.query(Item).filter(Item.id == item_id).first()


def update_item(db: Session, item: Item, item_data: ItemUpdate) -> Item:
    """Update an item."""
    if item_data.name is not None:
        item.name = item_data.name
    if item_data.description is not None:
        item.description = item_data.description
    if item_data.claim_limit is not None:
        item.claim_limit = item_data.claim_limit
    if item_data.require_details is not None:
        item.require_details = item_data.require_details
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: Item) -> None:
    """Delete an item (cascades to claims)."""
    db.delete(item)
    db.commit()


def can_claim_item(db: Session, item_id: int) -> bool:
    """Check if an item has available claim slots."""
    item = get_item(db, item_id)
    if not item:
        return False

    current_claims = db.query(Claim).filter(Claim.item_id == item_id).count()
    return current_claims < item.claim_limit


# Claim CRUD
def create_claim(db: Session, item: Item, claim_data: ClaimCreate) -> Claim:
    """Create a new claim for an item."""
    claim = Claim(
        item_id=item.id,
        attendee_name=claim_data.attendee_name,
        item_details=claim_data.item_details,
    )
    db.add(claim)
    db.commit()
    db.refresh(claim)
    return claim


def get_claim(db: Session, claim_id: int) -> Optional[Claim]:
    """Get a claim by ID."""
    return db.query(Claim).filter(Claim.id == claim_id).first()


def update_claim(db: Session, claim: Claim, claim_data: ClaimUpdate) -> Claim:
    """Update a claim."""
    if claim_data.attendee_name is not None:
        claim.attendee_name = claim_data.attendee_name
    if claim_data.item_details is not None:
        claim.item_details = claim_data.item_details

    db.commit()
    db.refresh(claim)
    return claim


def delete_claim(db: Session, claim: Claim) -> None:
    """Delete a claim."""
    db.delete(claim)
    db.commit()
