"""
Products API endpoints.
CRUD operations for tracked products using Firebase Firestore.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, HttpUrl

from database import ProductDB
from database.firebase_db import Platform

router = APIRouter(prefix="/products", tags=["products"])


# ============== Pydantic Schemas ==============

class ProductCreate(BaseModel):
    """Request body for creating a product."""
    url: HttpUrl
    price_alert_threshold: Optional[float] = None
    scrape_frequency_hours: int = 24


class ProductUpdate(BaseModel):
    """Request body for updating a product."""
    price_alert_threshold: Optional[float] = None
    scrape_frequency_hours: Optional[int] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Response model for a product."""
    id: str
    url: str
    platform: str
    name: Optional[str]
    image_url: Optional[str]
    current_price: Optional[float]
    currency: str
    in_stock: bool
    rating: Optional[float]
    review_count: Optional[int]
    seller_name: Optional[str]
    price_alert_threshold: Optional[float]
    lowest_price: Optional[float]
    highest_price: Optional[float]
    scrape_frequency_hours: int
    last_scraped_at: Optional[datetime]
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Response model for product list."""
    products: list[ProductResponse]
    total: int
    page: int
    page_size: int


def detect_platform(url: str) -> str:
    """Detect the e-commerce platform from a URL."""
    url_lower = url.lower()
    if "amazon" in url_lower:
        return Platform.AMAZON.value
    if "walmart" in url_lower:
        return Platform.WALMART.value
    if "target" in url_lower:
        return Platform.TARGET.value
    if "ebay" in url_lower:
        return Platform.EBAY.value
    return Platform.UNKNOWN.value


# ============== Endpoints ==============

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(data: ProductCreate):
    """
    Add a new product to track.
    
    - Detects platform from URL
    - Creates product record in Firestore
    """
    url_str = str(data.url)
    
    # Check if product already exists
    existing = await ProductDB.get_by_url(url_str)
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Product with this URL already exists"
        )
    
    # Detect platform
    platform = detect_platform(url_str)
    
    # Create product
    product = await ProductDB.create({
        "url": url_str,
        "platform": platform,
        "price_alert_threshold": data.price_alert_threshold,
        "scrape_frequency_hours": data.scrape_frequency_hours,
    })
    
    return product


@router.get("/", response_model=ProductListResponse)
async def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    platform: Optional[str] = None,
    active_only: bool = True,
):
    """
    Get all tracked products with pagination.
    """
    products, total = await ProductDB.list_all(
        page=page,
        page_size=page_size,
        platform=platform,
        active_only=active_only,
    )
    
    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a single product by ID."""
    product = await ProductDB.get_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, data: ProductUpdate):
    """Update a product's settings."""
    product = await ProductDB.get_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Build update dict
    update_data = {}
    if data.price_alert_threshold is not None:
        update_data["price_alert_threshold"] = data.price_alert_threshold
    if data.scrape_frequency_hours is not None:
        update_data["scrape_frequency_hours"] = data.scrape_frequency_hours
    if data.is_active is not None:
        update_data["is_active"] = data.is_active
    
    if update_data:
        product = await ProductDB.update(product_id, update_data)
    
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str):
    """Delete a product and all its history."""
    product = await ProductDB.get_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    await ProductDB.delete(product_id)
    return None
