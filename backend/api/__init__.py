"""API package for PriceWatch."""

from .products import router as products_router
from .scrape import router as scrape_router
from .history import router as history_router

__all__ = [
    "products_router",
    "scrape_router", 
    "history_router",
]
