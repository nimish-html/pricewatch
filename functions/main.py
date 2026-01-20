"""
PriceWatch - Scheduled Cloud Function for hourly price tracking.

This Firebase Cloud Function runs every hour via Google Cloud Scheduler
to trigger price scrapes for all tracked products, even when the main
backend is scaled down.
"""
from datetime import datetime, timedelta
from firebase_functions import scheduler_fn, logger
from firebase_admin import initialize_app, firestore
import requests

# Initialize Firebase Admin SDK
initialize_app()


@scheduler_fn.on_schedule(schedule="0 * * * *", timezone="UTC")
def hourly_price_tracker(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Scheduled function that runs every hour (at minute 0) to trigger price scrapes.
    
    This function:
    1. Reads all active products from Firestore
    2. Determines which products are due for scraping based on their frequency
    3. Calls the backend API to scrape each product
    
    The function runs independently of the Fly.io backend, ensuring scrapes
    happen even when the backend machine is scaled down.
    """
    logger.info("🕐 Starting scheduled price tracking...")
    
    db = firestore.client()
    now = datetime.utcnow()
    
    # Get all active products
    products_ref = db.collection("products")
    active_products = products_ref.where("is_active", "==", True).stream()
    
    backend_url = "https://pricewatch-api.fly.dev"
    successful = 0
    failed = 0
    skipped = 0
    
    for doc in active_products:
        product = doc.to_dict()
        product_id = doc.id
        
        # Check if product is due for scraping
        last_scraped = product.get("last_scraped_at")
        frequency_hours = product.get("scrape_frequency_hours", 24)
        
        # Determine if scrape is needed
        should_scrape = False
        if last_scraped is None:
            # Never scraped - definitely due
            should_scrape = True
        else:
            # Convert Firestore timestamp to datetime
            if hasattr(last_scraped, 'timestamp'):
                last_scraped = datetime.fromtimestamp(last_scraped.timestamp())
            next_scrape_time = last_scraped + timedelta(hours=frequency_hours)
            should_scrape = now >= next_scrape_time
        
        if not should_scrape:
            skipped += 1
            continue
        
        # Trigger scrape via backend API
        try:
            response = requests.post(
                f"{backend_url}/scrape/{product_id}",
                timeout=60  # Give scraper enough time
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    successful += 1
                    logger.info(f"✓ Scraped {product.get('name', product_id)}: ${data.get('current_price')}")
                else:
                    failed += 1
                    logger.warning(f"✗ Scrape failed for {product_id}: {data.get('error_message')}")
            else:
                failed += 1
                logger.warning(f"✗ HTTP {response.status_code} for {product_id}")
                
        except requests.Timeout:
            failed += 1
            logger.error(f"✗ Timeout scraping {product_id}")
        except Exception as e:
            failed += 1
            logger.error(f"✗ Error scraping {product_id}: {e}")
    
    logger.info(f"✓ Scheduled run complete: {successful} scraped, {failed} failed, {skipped} skipped (not due)")
