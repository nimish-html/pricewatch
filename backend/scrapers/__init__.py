"""Scrapers package for PriceWatch."""

from .base import BaseScraper, ScrapeResult
from .amazon import AmazonScraper
from .walmart import WalmartScraper
from .utils import get_random_headers, detect_platform

__all__ = [
    "BaseScraper",
    "ScrapeResult",
    "AmazonScraper",
    "WalmartScraper",
    "get_random_headers",
    "detect_platform",
]
