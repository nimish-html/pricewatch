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
                    
                    # --- Price Alert Logic ---
                    current_price = data.get('current_price')
                    alert_threshold = product.get('price_alert_threshold')
                    alert_email = product.get('alert_email')
                    
                    if current_price and alert_threshold and alert_email and current_price <= alert_threshold:
                        # Check cooldown (24h) to avoid spam
                        last_alert = product.get('last_alert_sent_at')
                        if hasattr(last_alert, 'timestamp'):
                            last_alert = datetime.fromtimestamp(last_alert.timestamp())
                        
                        # Send if never sent or > 24h ago
                        if not last_alert or (now - last_alert) > timedelta(hours=24):
                            try:
                                # Create email document
                                product_name = product.get('name') or 'Tracked Product'
                                product_url = product.get('url')
                                currency = product.get('currency', '$')
                                
                                db.collection("mail").add({
                                    "to": alert_email,
                                    "message": {
                                        "subject": f"⬇️ Price Drop: {product_name} is now {currency}{current_price}",
                                        "html": f"""
                                        <div style="font-family: sans-serif; max-width: 600px; margin: 0 auto;">
                                            <h2 style="color: #10b981;">Good news! A price you're watching has dropped.</h2>
                                            <p><strong>{product_name}</strong> is now available for <strong>{currency}{current_price}</strong>.</p>
                                            <p>Your target price was: {currency}{alert_threshold}</p>
                                            <div style="margin: 20px 0;">
                                                <a href="{product_url}" style="background-color: #000; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Deal</a>
                                            </div>
                                            <p style="font-size: 12px; color: #666;">
                                                You received this because you set a price alert on PriceWatch.
                                                We won't email you about this product again for at least 24 hours.
                                            </p>
                                        </div>
                                        """
                                    }
                                })
                                
                                # Update last_alert_sent_at
                                doc.reference.update({"last_alert_sent_at": now})
                                logger.info(f"📧 Sent alert to {alert_email} for {product_id}")
                                
                            except Exception as e:
                                logger.error(f"✗ Failed to send alert for {product_id}: {e}")
                    # -------------------------
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
