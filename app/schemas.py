"""Pydantic schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel, Field


# Potluck Schemas
class PotluckCreate(BaseModel):
    """Schema for creating a potluck."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class PotluckUpdate(BaseModel):
    """Schema for updating a potluck."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None


# Category Schemas
class CategoryCreate(BaseModel):
    """Schema for creating a category."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    max_items: int = Field(default=10, ge=1, le=100)
    display_order: int = Field(default=0, ge=0)


class CategoryUpdate(BaseModel):
    """Schema for updating a category."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    max_items: Optional[int] = Field(None, ge=1, le=100)
    display_order: Optional[int] = Field(None, ge=0)


# Item Schemas
class ItemCreate(BaseModel):
    """Schema for creating an item."""

    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    claim_limit: int = Field(default=1, ge=1, le=100)
    require_details: bool = Field(default=False)


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    claim_limit: Optional[int] = Field(None, ge=1, le=100)
    require_details: Optional[bool] = None


# Claim Schemas
class ClaimCreate(BaseModel):
    """Schema for creating a claim."""

    attendee_name: str = Field(..., min_length=1, max_length=200)
    item_details: Optional[str] = Field(None, max_length=500)


class ClaimUpdate(BaseModel):
    """Schema for updating a claim."""

    attendee_name: Optional[str] = Field(None, min_length=1, max_length=200)
    item_details: Optional[str] = Field(None, max_length=500)


# Admin Login Schema
class AdminLogin(BaseModel):
    """Schema for admin login."""

    password: str = Field(..., min_length=1)
