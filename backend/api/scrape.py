"""
Scrape API endpoints.
Trigger scrapes and view scraping stats using Firebase Firestore.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from database import ProductDB, PriceHistoryDB, ScrapeLogDB
from database.firebase_db import Platform, ScrapeStatus
from scrapers import AmazonScraper, WalmartScraper, ScrapeResult

router = APIRouter(prefix="/scrape", tags=["scrape"])


# ============== Pydantic Schemas ==============

class ScrapeResponse(BaseModel):
    """Response after triggering a scrape."""
    product_id: str
    success: bool
    name: Optional[str]
    current_price: Optional[float]
    in_stock: bool
    response_time_ms: int
    error_message: Optional[str]


class ScrapeStatsResponse(BaseModel):
    """Scraping statistics."""
    total_scrapes: int
    successful_scrapes: int
    failed_scrapes: int
    blocked_scrapes: int
    success_rate: float
    avg_response_time_ms: float
    platforms: dict[str, dict]


# ============== Helper Functions ==============

def get_scraper_for_platform(platform: str):
    """Get the appropriate scraper for a platform."""
    scrapers = {
        Platform.AMAZON.value: AmazonScraper,
        Platform.WALMART.value: WalmartScraper,
    }
    scraper_class = scrapers.get(platform)
    if scraper_class:
        return scraper_class()
    return None


async def perform_scrape(product_id: str) -> ScrapeResult | None:
    """
    Perform a scrape for a product and update Firestore.
    
    Returns the scrape result or None if product not found.
    """
    # Get product
    product = await ProductDB.get_by_id(product_id)
    
    if not product:
        return None
    
    # Get scraper
    scraper = get_scraper_for_platform(product["platform"])
    if not scraper:
        # Log unsupported platform
        await ScrapeLogDB.add(product_id, {
            "status": ScrapeStatus.FAILED.value,
            "error_message": f"Unsupported platform: {product['platform']}",
        })
        return ScrapeResult(
            success=False,
            platform=Platform(product["platform"]),
            status=ScrapeStatus.FAILED,
            error_message=f"Unsupported platform: {product['platform']}",
        )
    
    try:
        # Perform scrape
        scrape_result = await scraper.scrape(product["url"])
        
        # Update product if successful
        if scrape_result.success:
            update_data = {
                "name": scrape_result.name or product.get("name"),
                "current_price": scrape_result.current_price,
                "currency": scrape_result.currency,
                "in_stock": scrape_result.in_stock,
                "image_url": scrape_result.image_url or product.get("image_url"),
                "rating": scrape_result.rating or product.get("rating"),
                "review_count": scrape_result.review_count or product.get("review_count"),
                "seller_name": scrape_result.seller_name or product.get("seller_name"),
                "last_scraped_at": datetime.utcnow(),
            }
            
            # Update price history tracking
            if scrape_result.current_price:
                lowest = product.get("lowest_price")
                highest = product.get("highest_price")
                
                if lowest is None or scrape_result.current_price < lowest:
                    update_data["lowest_price"] = scrape_result.current_price
                if highest is None or scrape_result.current_price > highest:
                    update_data["highest_price"] = scrape_result.current_price
            
            await ProductDB.update(product_id, update_data)
            
            # Add price history record
            await PriceHistoryDB.add(product_id, {
                "price": scrape_result.current_price,
                "currency": scrape_result.currency,
                "in_stock": scrape_result.in_stock,
            })
        
        # Log the scrape
        await ScrapeLogDB.add(product_id, {
            "status": scrape_result.status.value,
            "response_time_ms": scrape_result.response_time_ms,
            "error_message": scrape_result.error_message,
            "http_status_code": scrape_result.http_status_code,
        })
        
        return scrape_result
        
    except Exception as e:
        # Log error
        await ScrapeLogDB.add(product_id, {
            "status": ScrapeStatus.FAILED.value,
            "error_message": str(e),
        })
        raise
    
    finally:
        await scraper.close()


# ============== Endpoints ==============

@router.post("/{product_id}", response_model=ScrapeResponse)
async def trigger_scrape(product_id: str):
    """
    Trigger an immediate scrape for a product.
    """
    result = await perform_scrape(product_id)
    
    if result is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return ScrapeResponse(
        product_id=product_id,
        success=result.success,
        name=result.name,
        current_price=result.current_price,
        in_stock=result.in_stock,
        response_time_ms=result.response_time_ms,
        error_message=result.error_message,
    )


@router.post("/batch", response_model=list[ScrapeResponse])
async def trigger_batch_scrape(product_ids: list[str]):
    """
    Trigger scrapes for multiple products (max 10).
    """
    if len(product_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 products per batch."
        )
    
    results = []
    for product_id in product_ids:
        result = await perform_scrape(product_id)
        if result:
            results.append(ScrapeResponse(
                product_id=product_id,
                success=result.success,
                name=result.name,
                current_price=result.current_price,
                in_stock=result.in_stock,
                response_time_ms=result.response_time_ms,
                error_message=result.error_message,
            ))
    
    return results


@router.get("/stats", response_model=ScrapeStatsResponse)
async def get_scrape_stats():
    """
    Get scraping statistics.
    """
    stats = await ScrapeLogDB.get_stats()
    
    # Add platform info
    platforms = {}
    for platform in Platform:
        if platform != Platform.UNKNOWN:
            platforms[platform.value] = {
                "name": platform.value.title(),
                "supported": platform in [Platform.AMAZON, Platform.WALMART],
            }
    
    return ScrapeStatsResponse(
        total_scrapes=stats["total_scrapes"],
        successful_scrapes=stats["successful_scrapes"],
        failed_scrapes=stats["failed_scrapes"],
        blocked_scrapes=stats["blocked_scrapes"],
        success_rate=stats["success_rate"],
        avg_response_time_ms=stats["avg_response_time_ms"],
        platforms=platforms,
    )
