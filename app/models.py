"""Database models for the potluck organizer."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Potluck(Base):
    """Potluck event model."""

    __tablename__ = "potlucks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    url_slug = Column(String(100), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    categories = relationship("Category", back_populates="potluck", cascade="all, delete-orphan")


class Category(Base):
    """Category model for grouping items."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    potluck_id = Column(Integer, ForeignKey("potlucks.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    display_order = Column(Integer, default=0)

    # Relationships
    potluck = relationship("Potluck", back_populates="categories")
    items = relationship("Item", back_populates="category", cascade="all, delete-orphan")


class Item(Base):
    """Item model for things to bring to potluck."""

    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    claim_limit = Column(Integer, nullable=False, default=1)
    created_by_admin = Column(Boolean, default=True)
    require_details = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    category = relationship("Category", back_populates="items")
    claims = relationship("Claim", back_populates="item", cascade="all, delete-orphan")


class Claim(Base):
    """Claim model for attendees claiming items."""

    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    attendee_name = Column(String(200), nullable=False)
    item_details = Column(Text, nullable=True)
    session_id = Column(String(255), nullable=True)  # Session ID to track who created the claim
    claimed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    item = relationship("Item", back_populates="claims")
