"""
Firebase Firestore database layer for PriceWatch.

Collections:
- products: Tracked products with current price
- price_history: Historical price records (subcollection of products)
- scrape_logs: Scraping activity logs (subcollection of products)
"""
from __future__ import annotations

import os
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Optional
from enum import Enum

from config import get_settings

# Global Firestore client
_db: Optional[firestore.Client] = None


class Platform(str, Enum):
    """Supported e-commerce platforms."""
    AMAZON = "amazon"
    WALMART = "walmart"
    TARGET = "target"
    EBAY = "ebay"
    UNKNOWN = "unknown"


class ScrapeStatus(str, Enum):
    """Status of a scrape operation."""
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"
    TIMEOUT = "timeout"


def init_firebase() -> None:
    """Initialize Firebase Admin SDK."""
    global _db
    
    if _db is not None:
        return  # Already initialized
    
    settings = get_settings()
    
    # Option 1: Use file path to service account JSON (only if file exists)
    if settings.google_application_credentials and os.path.exists(settings.google_application_credentials):
        cred = credentials.Certificate(settings.google_application_credentials)
        firebase_admin.initialize_app(cred)
    # Option 2: Use inline JSON credentials (for cloud deployments like Fly.io)
    elif creds := settings.get_firebase_credentials():
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)
    else:
        # Try default credentials
        try:
            firebase_admin.initialize_app()
        except ValueError:
            pass  # Already initialized
    
    _db = firestore.client()


def get_db() -> firestore.Client:
    """Get Firestore client instance."""
    global _db
    if _db is None:
        init_firebase()
    return _db


class ProductDB:
    """Database operations for products."""
    
    COLLECTION = "products"
    
    @staticmethod
    def _to_dict(doc_snapshot) -> dict:
        """Convert Firestore document to dict with ID."""
        if not doc_snapshot.exists:
            return None
        data = doc_snapshot.to_dict()
        data["id"] = doc_snapshot.id
        return data
    
    @classmethod
    async def create(cls, data: dict) -> dict:
        """Create a new product."""
        db = get_db()
        
        # Set defaults and timestamps
        now = datetime.utcnow()
        product_data = {
            "url": data["url"],
            "platform": data.get("platform", Platform.UNKNOWN.value),
            "name": data.get("name"),
            "image_url": data.get("image_url"),
            "current_price": data.get("current_price"),
            "currency": data.get("currency", "USD"),
            "in_stock": data.get("in_stock", True),
            "rating": data.get("rating"),
            "review_count": data.get("review_count"),
            "seller_name": data.get("seller_name"),
            "price_alert_threshold": data.get("price_alert_threshold"),
            "lowest_price": data.get("lowest_price"),
            "highest_price": data.get("highest_price"),
            "scrape_frequency_hours": data.get("scrape_frequency_hours", 24),
            "last_scraped_at": None,
            "created_at": now,
            "updated_at": now,
            "is_active": True,
        }
        
        # Add to Firestore
        doc_ref = db.collection(cls.COLLECTION).add(product_data)
        product_data["id"] = doc_ref[1].id
        
        return product_data
    
    @classmethod
    async def get_by_id(cls, product_id: str) -> dict | None:
        """Get a product by ID."""
        db = get_db()
        doc = db.collection(cls.COLLECTION).document(product_id).get()
        return cls._to_dict(doc)
    
    @classmethod
    async def get_by_url(cls, url: str) -> dict | None:
        """Get a product by URL."""
        db = get_db()
        docs = db.collection(cls.COLLECTION).where("url", "==", url).limit(1).get()
        for doc in docs:
            return cls._to_dict(doc)
        return None
    
    @classmethod
    async def list_all(
        cls,
        page: int = 1,
        page_size: int = 20,
        platform: str | None = None,
        active_only: bool = True,
    ) -> tuple[list[dict], int]:
        """List products with pagination."""
        db = get_db()
        query = db.collection(cls.COLLECTION)
        
        # Get all docs and filter/sort in memory to avoid composite index issues
        all_docs = list(query.get())
        
        # Filter by is_active
        if active_only:
            all_docs = [doc for doc in all_docs if doc.to_dict().get("is_active", True)]
        
        # Filter by platform
        if platform:
            all_docs = [doc for doc in all_docs if doc.to_dict().get("platform") == platform]
        
        total = len(all_docs)
        
        # Sort by created_at descending
        all_docs.sort(key=lambda d: d.to_dict().get("created_at", datetime.min), reverse=True)
        
        # Paginate
        start = (page - 1) * page_size
        end = start + page_size
        paginated_docs = all_docs[start:end]
        
        products = [cls._to_dict(doc) for doc in paginated_docs]
        
        return products, total
    
    @classmethod
    async def update(cls, product_id: str, data: dict) -> dict | None:
        """Update a product."""
        db = get_db()
        doc_ref = db.collection(cls.COLLECTION).document(product_id)
        
        # Add updated timestamp
        data["updated_at"] = datetime.utcnow()
        
        doc_ref.update(data)
        return await cls.get_by_id(product_id)
    
    @classmethod
    async def delete(cls, product_id: str) -> bool:
        """Delete a product and its subcollections."""
        db = get_db()
        doc_ref = db.collection(cls.COLLECTION).document(product_id)
        
        # Delete subcollections first
        for subcol in ["price_history", "scrape_logs"]:
            subcol_ref = doc_ref.collection(subcol)
            for doc in subcol_ref.get():
                doc.reference.delete()
        
        # Delete the product
        doc_ref.delete()
        return True


class PriceHistoryDB:
    """Database operations for price history."""
    
    @classmethod
    async def add(cls, product_id: str, data: dict) -> dict:
        """Add a price history record."""
        db = get_db()
        
        history_data = {
            "price": data["price"],
            "currency": data.get("currency", "USD"),
            "in_stock": data.get("in_stock", True),
            "recorded_at": datetime.utcnow(),
        }
        
        doc_ref = db.collection(ProductDB.COLLECTION).document(product_id) \
                    .collection("price_history").add(history_data)
        
        history_data["id"] = doc_ref[1].id
        history_data["product_id"] = product_id
        return history_data
    
    @classmethod
    async def get_history(
        cls,
        product_id: str,
        limit: int = 100,
        since: datetime | None = None,
    ) -> list[dict]:
        """Get price history for a product."""
        db = get_db()
        query = db.collection(ProductDB.COLLECTION).document(product_id) \
                  .collection("price_history")
        
        if since:
            query = query.where("recorded_at", ">=", since)
        
        query = query.order_by("recorded_at", direction=firestore.Query.ASCENDING)
        query = query.limit(limit)
        
        docs = query.get()
        return [{"id": doc.id, "product_id": product_id, **doc.to_dict()} for doc in docs]


class ScrapeLogDB:
    """Database operations for scrape logs."""
    
    @classmethod
    async def add(cls, product_id: str, data: dict) -> dict:
        """Add a scrape log record."""
        db = get_db()
        
        log_data = {
            "status": data["status"],
            "response_time_ms": data.get("response_time_ms"),
            "proxy_used": data.get("proxy_used"),
            "error_message": data.get("error_message"),
            "http_status_code": data.get("http_status_code"),
            "created_at": datetime.utcnow(),
        }
        
        doc_ref = db.collection(ProductDB.COLLECTION).document(product_id) \
                    .collection("scrape_logs").add(log_data)
        
        log_data["id"] = doc_ref[1].id
        log_data["product_id"] = product_id
        return log_data
    
    @classmethod
    async def get_logs(cls, product_id: str, limit: int = 50) -> list[dict]:
        """Get scrape logs for a product."""
        db = get_db()
        query = db.collection(ProductDB.COLLECTION).document(product_id) \
                  .collection("scrape_logs")
        
        query = query.order_by("created_at", direction=firestore.Query.DESCENDING)
        query = query.limit(limit)
        
        docs = query.get()
        return [{"id": doc.id, "product_id": product_id, **doc.to_dict()} for doc in docs]
    
    @classmethod
    async def get_stats(cls) -> dict:
        """Get aggregate scraping statistics."""
        db = get_db()
        
        # This is a simplified version - for production, use aggregation queries
        # or maintain a separate stats collection
        stats = {
            "total_scrapes": 0,
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "blocked_scrapes": 0,
            "total_response_time_ms": 0,
        }
        
        # Get all products and their recent logs
        products = db.collection(ProductDB.COLLECTION).get()
        
        for product in products:
            logs = product.reference.collection("scrape_logs").limit(100).get()
            for log in logs:
                data = log.to_dict()
                stats["total_scrapes"] += 1
                
                status = data.get("status", "")
                if status == ScrapeStatus.SUCCESS.value:
                    stats["successful_scrapes"] += 1
                elif status == ScrapeStatus.BLOCKED.value:
                    stats["blocked_scrapes"] += 1
                else:
                    stats["failed_scrapes"] += 1
                
                if data.get("response_time_ms"):
                    stats["total_response_time_ms"] += data["response_time_ms"]
        
        # Calculate averages
        if stats["total_scrapes"] > 0:
            stats["success_rate"] = round(
                (stats["successful_scrapes"] / stats["total_scrapes"]) * 100, 2
            )
            stats["avg_response_time_ms"] = round(
                stats["total_response_time_ms"] / stats["total_scrapes"], 2
            )
        else:
            stats["success_rate"] = 0
            stats["avg_response_time_ms"] = 0
        
        del stats["total_response_time_ms"]
        return stats
