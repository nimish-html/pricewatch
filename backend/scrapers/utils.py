"""
Utility functions for scrapers.
Includes user agent rotation, header generation, and platform detection.
"""
from __future__ import annotations

import random
import re
from urllib.parse import urlparse
from database.firebase_db import Platform

# Common user agents - updated for 2026
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
]

# Common accept headers
ACCEPT_HEADERS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
]

ACCEPT_LANGUAGE = [
    "en-US,en;q=0.9",
    "en-US,en;q=0.8",
    "en-GB,en;q=0.9,en-US;q=0.8",
]


def get_random_headers(referer: str | None = None) -> dict[str, str]:
    """
    Generate randomized browser-like headers for anti-detection.
    
    Args:
        referer: Optional referer URL
        
    Returns:
        Dictionary of headers
    """
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": random.choice(ACCEPT_HEADERS),
        "Accept-Language": random.choice(ACCEPT_LANGUAGE),
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none" if not referer else "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    if referer:
        headers["Referer"] = referer
    
    return headers


def detect_platform(url: str) -> Platform:
    """
    Detect the e-commerce platform from a URL.
    
    Args:
        url: Product URL
        
    Returns:
        Platform enum value
    """
    parsed = urlparse(url.lower())
    domain = parsed.netloc
    
    # Remove www. prefix
    if domain.startswith("www."):
        domain = domain[4:]
    
    # Amazon (multiple TLDs)
    if re.match(r"amazon\.(com|co\.uk|de|fr|it|es|ca|com\.au|in|jp|com\.mx|com\.br)", domain):
        return Platform.AMAZON
    
    # Walmart
    if "walmart.com" in domain:
        return Platform.WALMART
    
    # Target
    if "target.com" in domain:
        return Platform.TARGET
    
    # eBay
    if re.match(r"ebay\.(com|co\.uk|de|fr|it|es|ca|com\.au)", domain):
        return Platform.EBAY
    
    return Platform.UNKNOWN


def extract_price(text: str) -> float | None:
    """
    Extract price from a text string.
    Handles various formats: $29.99, $1,299.00, etc.
    
    Args:
        text: Text containing price
        
    Returns:
        Float price or None if not found
    """
    if not text:
        return None
    
    # Remove common currency symbols and whitespace
    clean = text.strip().replace(",", "").replace(" ", "")
    
    # Match price patterns
    match = re.search(r"[\$£€]?(\d+(?:\.\d{2})?)", clean)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    
    return None


def extract_rating(text: str) -> float | None:
    """
    Extract rating from text like "4.5 out of 5 stars".
    
    Args:
        text: Text containing rating
        
    Returns:
        Float rating or None
    """
    if not text:
        return None
    
    match = re.search(r"(\d+(?:\.\d+)?)\s*(?:out of|/)\s*5", text.lower())
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    
    # Try simple decimal pattern
    match = re.search(r"^(\d+(?:\.\d+)?)\s*$", text.strip())
    if match:
        rating = float(match.group(1))
        if 0 <= rating <= 5:
            return rating
    
    return None


def extract_review_count(text: str) -> int | None:
    """
    Extract review count from text like "1,234 ratings" or "(1234)".
    
    Args:
        text: Text containing review count
        
    Returns:
        Integer count or None
    """
    if not text:
        return None
    
    clean = text.replace(",", "").replace("(", "").replace(")", "")
    match = re.search(r"(\d+)", clean)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            return None
    
    return None
