"""Database package for PriceWatch - Firebase Firestore."""

from .firebase_db import (
    init_firebase,
    get_db,
    ProductDB,
    PriceHistoryDB,
    ScrapeLogDB,
)

__all__ = [
    "init_firebase",
    "get_db",
    "ProductDB",
    "PriceHistoryDB",
    "ScrapeLogDB",
]
