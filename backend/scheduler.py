"""
Background scheduler for automatic price tracking.

Uses APScheduler to run periodic scraping jobs based on each product's
configured scrape_frequency_hours setting.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from database import ProductDB, get_db
from api.scrape import perform_scrape

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global scheduler instance
_scheduler: Optional[AsyncIOScheduler] = None


async def get_products_due_for_scrape() -> list[dict]:
    """
    Get all products that are due for scraping based on their
    scrape_frequency_hours and last_scraped_at timestamp.
    """
    db = get_db()
    now = datetime.utcnow()
    
    # Get all active products
    all_docs = db.collection(ProductDB.COLLECTION).get()
    
    products_due = []
    for doc in all_docs:
        data = doc.to_dict()
        data["id"] = doc.id
        
        # Skip inactive products
        if not data.get("is_active", True):
            continue
        
        # Check if due for scraping
        last_scraped = data.get("last_scraped_at")
        frequency_hours = data.get("scrape_frequency_hours", 24)
        
        if last_scraped is None:
            # Never scraped - definitely due
            products_due.append(data)
        else:
            # Convert Firebase timestamp to datetime if needed
            if hasattr(last_scraped, 'timestamp'):
                last_scraped = datetime.fromtimestamp(last_scraped.timestamp())
            
            # Check if enough time has passed
            next_scrape_time = last_scraped + timedelta(hours=frequency_hours)
            if now >= next_scrape_time:
                products_due.append(data)
    
    return products_due


async def run_scheduled_scrapes():
    """
    Main scheduled job - scrapes all products that are due.
    
    This runs every hour and checks which products need scraping
    based on their individual scrape_frequency_hours setting.
    """
    logger.info("🕐 Starting scheduled scrape run...")
    
    try:
        products = await get_products_due_for_scrape()
        
        if not products:
            logger.info("✓ No products due for scraping")
            return
        
        logger.info(f"📦 Found {len(products)} products due for scraping")
        
        # Scrape each product with a delay to avoid rate limiting
        successful = 0
        failed = 0
        
        for product in products:
            try:
                logger.info(f"  → Scraping {product.get('name', product['id'])}...")
                result = await perform_scrape(product["id"])
                
                if result and result.success:
                    successful += 1
                    logger.info(f"    ✓ Success: ${result.current_price}")
                else:
                    failed += 1
                    error_msg = result.error_message if result else "Unknown error"
                    logger.warning(f"    ✗ Failed: {error_msg}")
                
                # Add delay between scrapes (2-5 seconds)
                await asyncio.sleep(3)
                
            except Exception as e:
                failed += 1
                logger.error(f"    ✗ Error scraping {product['id']}: {e}")
        
        logger.info(f"✓ Scheduled scrape complete: {successful} successful, {failed} failed")
        
    except Exception as e:
        logger.error(f"✗ Scheduled scrape error: {e}")


def start_scheduler() -> AsyncIOScheduler:
    """
    Start the background scheduler.
    
    Runs the scraping job every hour to check which products need updating.
    """
    global _scheduler
    
    if _scheduler is not None:
        return _scheduler
    
    _scheduler = AsyncIOScheduler()
    
    # Add the main scraping job - runs every hour
    _scheduler.add_job(
        run_scheduled_scrapes,
        trigger=IntervalTrigger(hours=1),
        id="scheduled_scrapes",
        name="Hourly price check",
        replace_existing=True,
    )
    
    # Run an immediate check on startup (after 30 seconds delay)
    _scheduler.add_job(
        run_scheduled_scrapes,
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=30),
        id="startup_scrape",
        name="Startup price check",
    )
    
    _scheduler.start()
    logger.info("✓ Background scheduler started (checking every hour)")
    
    return _scheduler


def stop_scheduler():
    """Stop the background scheduler."""
    global _scheduler
    
    if _scheduler is not None:
        _scheduler.shutdown(wait=False)
        _scheduler = None
        logger.info("✓ Background scheduler stopped")


def get_scheduler() -> Optional[AsyncIOScheduler]:
    """Get the current scheduler instance."""
    return _scheduler
