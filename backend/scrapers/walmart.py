"""
Walmart product scraper.
Extracts product data from Walmart product pages.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
import json
import re
from database.firebase_db import Platform, ScrapeStatus
from .base import BaseScraper, ScrapeResult
from .utils import extract_price


class WalmartScraper(BaseScraper):
    """Scraper for Walmart product pages."""
    
    platform = Platform.WALMART
    
    async def parse(self, html: str, url: str) -> ScrapeResult:
        """
        Parse Walmart product page HTML.
        
        Walmart uses a lot of JavaScript data, so we try to extract
        from both HTML elements and embedded JSON-LD/script data.
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Try to extract from JSON-LD first (more reliable)
        json_data = self._extract_json_ld(soup)
        
        if json_data:
            return self._parse_from_json(json_data, soup, url)
        
        # Fallback to HTML parsing
        return self._parse_from_html(soup, url)
    
    def _extract_json_ld(self, soup: BeautifulSoup) -> dict | None:
        """Extract product data from JSON-LD script tag."""
        scripts = soup.find_all("script", {"type": "application/ld+json"})
        
        for script in scripts:
            try:
                data = json.loads(script.string)
                
                # Handle array of schemas
                if isinstance(data, list):
                    for item in data:
                        if item.get("@type") == "Product":
                            return item
                
                # Direct product schema
                if data.get("@type") == "Product":
                    return data
                    
            except (json.JSONDecodeError, TypeError):
                continue
        
        return None
    
    def _parse_from_json(self, data: dict, soup: BeautifulSoup, url: str) -> ScrapeResult:
        """Parse product data from JSON-LD schema."""
        name = data.get("name")
        
        # Extract price from offers
        price = None
        currency = "USD"
        in_stock = True
        
        offers = data.get("offers", {})
        if isinstance(offers, list):
            offers = offers[0] if offers else {}
        
        if offers:
            price_str = offers.get("price")
            if price_str:
                try:
                    price = float(price_str)
                except (ValueError, TypeError):
                    price = extract_price(str(price_str))
            
            currency = offers.get("priceCurrency", "USD")
            availability = offers.get("availability", "")
            in_stock = "InStock" in availability or "instock" in availability.lower()
        
        # Extract rating
        rating = None
        review_count = None
        aggregate_rating = data.get("aggregateRating", {})
        if aggregate_rating:
            try:
                rating = float(aggregate_rating.get("ratingValue", 0))
            except (ValueError, TypeError):
                pass
            try:
                review_count = int(aggregate_rating.get("reviewCount", 0))
            except (ValueError, TypeError):
                pass
        
        # Extract image
        image_url = None
        images = data.get("image")
        if isinstance(images, list) and images:
            image_url = images[0]
        elif isinstance(images, str):
            image_url = images
        
        # Extract seller from HTML since JSON-LD doesn't include it
        seller_name = self._extract_seller_html(soup)
        
        success = name is not None and price is not None
        
        return ScrapeResult(
            success=success,
            platform=self.platform,
            name=name,
            current_price=price,
            currency=currency,
            in_stock=in_stock,
            image_url=image_url,
            rating=rating,
            review_count=review_count,
            seller_name=seller_name,
            status=ScrapeStatus.SUCCESS if success else ScrapeStatus.FAILED,
            error_message=None if success else "Could not extract product data",
        )
    
    def _parse_from_html(self, soup: BeautifulSoup, url: str) -> ScrapeResult:
        """Fallback HTML parsing for Walmart pages."""
        # Extract name
        name = self._extract_name_html(soup)
        
        # Extract price
        price = self._extract_price_html(soup)
        
        # Check availability
        in_stock = self._check_availability_html(soup)
        
        # Extract rating
        rating = self._extract_rating_html(soup)
        
        # Extract review count
        review_count = self._extract_review_count_html(soup)
        
        # Extract seller
        seller_name = self._extract_seller_html(soup)
        
        # Extract image
        image_url = self._extract_image_html(soup)
        
        success = name is not None and price is not None
        
        return ScrapeResult(
            success=success,
            platform=self.platform,
            name=name,
            current_price=price,
            currency="USD",
            in_stock=in_stock,
            image_url=image_url,
            rating=rating,
            review_count=review_count,
            seller_name=seller_name,
            status=ScrapeStatus.SUCCESS if success else ScrapeStatus.FAILED,
            error_message=None if success else "Could not extract product data from HTML",
        )
    
    def _extract_name_html(self, soup: BeautifulSoup) -> str | None:
        """Extract product name from HTML."""
        # Primary: h1 with product name
        h1 = soup.find("h1", {"itemprop": "name"})
        if h1:
            return h1.get_text(strip=True)
        
        # Alternative: data attribute
        name_el = soup.find(attrs={"data-testid": "product-title"})
        if name_el:
            return name_el.get_text(strip=True)
        
        # Fallback: first h1
        h1 = soup.find("h1")
        if h1:
            return h1.get_text(strip=True)
        
        return None
    
    def _extract_price_html(self, soup: BeautifulSoup) -> float | None:
        """Extract price from HTML."""
        # Look for price with itemprop
        price_el = soup.find(attrs={"itemprop": "price"})
        if price_el:
            content = price_el.get("content")
            if content:
                try:
                    return float(content)
                except ValueError:
                    pass
            return extract_price(price_el.get_text())
        
        # Look for price display
        price_display = soup.find(attrs={"data-testid": "price-wrap"})
        if price_display:
            price_span = price_display.find("span", class_=re.compile("price"))
            if price_span:
                return extract_price(price_span.get_text())
        
        # Look for any element with dollar amount
        for el in soup.find_all("span"):
            text = el.get_text(strip=True)
            if text.startswith("$") and len(text) < 20:
                price = extract_price(text)
                if price and price > 0:
                    return price
        
        return None
    
    def _check_availability_html(self, soup: BeautifulSoup) -> bool:
        """Check product availability from HTML."""
        # Look for out of stock indicators
        oos_el = soup.find(text=re.compile(r"out of stock|sold out|unavailable", re.I))
        if oos_el:
            return False
        
        # Check for add to cart button
        add_btn = soup.find("button", text=re.compile(r"add to cart", re.I))
        if add_btn:
            return True
        
        return True  # Default to in stock
    
    def _extract_rating_html(self, soup: BeautifulSoup) -> float | None:
        """Extract rating from HTML."""
        # Look for rating with itemprop
        rating_el = soup.find(attrs={"itemprop": "ratingValue"})
        if rating_el:
            content = rating_el.get("content")
            if content:
                try:
                    return float(content)
                except ValueError:
                    pass
        
        # Look for rating display
        rating_span = soup.find("span", class_=re.compile("rating"))
        if rating_span:
            text = rating_span.get_text(strip=True)
            match = re.search(r"(\d+(?:\.\d+)?)", text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _extract_review_count_html(self, soup: BeautifulSoup) -> int | None:
        """Extract review count from HTML."""
        # Look for review count with itemprop
        count_el = soup.find(attrs={"itemprop": "reviewCount"})
        if count_el:
            content = count_el.get("content")
            if content:
                try:
                    return int(content)
                except ValueError:
                    pass
        
        # Look for reviews link
        reviews_link = soup.find("a", text=re.compile(r"\d+\s*reviews?", re.I))
        if reviews_link:
            text = reviews_link.get_text()
            match = re.search(r"(\d+)", text.replace(",", ""))
            if match:
                try:
                    return int(match.group(1))
                except ValueError:
                    pass
        
        return None
    
    def _extract_seller_html(self, soup: BeautifulSoup) -> str | None:
        """Extract seller name from HTML."""
        # Look for sold by section
        sold_by = soup.find(text=re.compile(r"sold by", re.I))
        if sold_by:
            parent = sold_by.find_parent()
            if parent:
                link = parent.find("a")
                if link:
                    return link.get_text(strip=True)
                # Get text after "Sold by"
                text = parent.get_text(strip=True)
                match = re.search(r"sold by\s+(.+?)(?:\s*\||\s*$)", text, re.I)
                if match:
                    return match.group(1).strip()
        
        return None
    
    def _extract_image_html(self, soup: BeautifulSoup) -> str | None:
        """Extract product image from HTML."""
        # Look for main product image
        img = soup.find("img", attrs={"data-testid": "hero-image"})
        if img and img.get("src"):
            return img["src"]
        
        # Look for image with itemprop
        img = soup.find("img", attrs={"itemprop": "image"})
        if img and img.get("src"):
            return img["src"]
        
        # Fallback to first large image
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "product" in src.lower() and ("large" in src.lower() or "xlarge" in src.lower()):
                return src
        
        return None
