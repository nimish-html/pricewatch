"""
Amazon product scraper.
Extracts product data from Amazon product pages.
"""
from __future__ import annotations

from bs4 import BeautifulSoup
from database.firebase_db import Platform, ScrapeStatus
from .base import BaseScraper, ScrapeResult
from .utils import extract_price, extract_rating, extract_review_count


class AmazonScraper(BaseScraper):
    """Scraper for Amazon product pages."""
    
    platform = Platform.AMAZON
    
    async def parse(self, html: str, url: str) -> ScrapeResult:
        """
        Parse Amazon product page HTML.
        
        Handles various Amazon page layouts for:
        - Product name
        - Price (deal price, regular price)
        - Availability
        - Rating and review count
        - Seller info
        - Product image
        """
        soup = BeautifulSoup(html, "lxml")
        
        # Detect currency from URL domain
        currency = self._detect_currency(url)
        
        # Extract product name
        name = self._extract_name(soup)
        
        # Extract price
        price = self._extract_price(soup)
        
        # Check availability
        in_stock = self._check_availability(soup)
        
        # Extract rating
        rating = self._extract_rating(soup)
        
        # Extract review count
        review_count = self._extract_review_count(soup)
        
        # Extract seller
        seller_name = self._extract_seller(soup)
        
        # Extract image
        image_url = self._extract_image(soup)
        
        # Determine success
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
    
    def _detect_currency(self, url: str) -> str:
        """Detect currency based on Amazon domain."""
        url_lower = url.lower()
        if "amazon.in" in url_lower:
            return "INR"
        if "amazon.co.uk" in url_lower:
            return "GBP"
        if "amazon.de" in url_lower or "amazon.fr" in url_lower or "amazon.it" in url_lower or "amazon.es" in url_lower:
            return "EUR"
        if "amazon.ca" in url_lower:
            return "CAD"
        if "amazon.com.au" in url_lower:
            return "AUD"
        if "amazon.co.jp" in url_lower:
            return "JPY"
        if "amazon.com.mx" in url_lower:
            return "MXN"
        if "amazon.com.br" in url_lower:
            return "BRL"
        return "USD"  # Default for amazon.com
    
    def _extract_name(self, soup: BeautifulSoup) -> str | None:
        """Extract product name from various possible elements."""
        # Primary: productTitle span
        title_el = soup.find("span", {"id": "productTitle"})
        if title_el:
            return title_el.get_text(strip=True)
        
        # Alternative: title tag in header
        title_el = soup.find("h1", {"id": "title"})
        if title_el:
            return title_el.get_text(strip=True)
        
        # Fallback: meta title
        meta_title = soup.find("meta", {"name": "title"})
        if meta_title and meta_title.get("content"):
            return meta_title["content"]
        
        return None
    
    def _extract_price(self, soup: BeautifulSoup) -> float | None:
        """Extract price, preferring deal price over regular price."""
        # Deal price (apex price)
        price_el = soup.find("span", {"class": "a-price-whole"})
        if price_el:
            whole = price_el.get_text(strip=True).replace(",", "").replace(".", "")
            fraction_el = soup.find("span", {"class": "a-price-fraction"})
            fraction = fraction_el.get_text(strip=True) if fraction_el else "00"
            try:
                return float(f"{whole}.{fraction}")
            except ValueError:
                pass
        
        # Core price (corePrice_feature_div)
        core_price = soup.find("div", {"id": "corePrice_feature_div"})
        if core_price:
            price_span = core_price.find("span", {"class": "a-offscreen"})
            if price_span:
                return extract_price(price_span.get_text())
        
        # Alternative: price block
        price_block = soup.find("span", {"id": "priceblock_ourprice"})
        if price_block:
            return extract_price(price_block.get_text())
        
        # Deal price block
        deal_price = soup.find("span", {"id": "priceblock_dealprice"})
        if deal_price:
            return extract_price(deal_price.get_text())
        
        # Kindle/ebook price
        kindle_price = soup.find("span", {"id": "kindle-price"})
        if kindle_price:
            return extract_price(kindle_price.get_text())
        
        return None
    
    def _check_availability(self, soup: BeautifulSoup) -> bool:
        """Check if product is in stock."""
        # Check availability div
        availability = soup.find("div", {"id": "availability"})
        if availability:
            text = availability.get_text(strip=True).lower()
            if "in stock" in text:
                return True
            if "out of stock" in text or "currently unavailable" in text:
                return False
        
        # Check add to cart button presence
        add_to_cart = soup.find("input", {"id": "add-to-cart-button"})
        if add_to_cart:
            return True
        
        # Default to in stock if we can't determine
        return True
    
    def _extract_rating(self, soup: BeautifulSoup) -> float | None:
        """Extract star rating."""
        # Rating in CR widget
        rating_el = soup.find("span", {"class": "a-icon-alt"})
        if rating_el:
            text = rating_el.get_text()
            return extract_rating(text)
        
        # Alternative: customer review section
        review_section = soup.find("div", {"id": "averageCustomerReviews"})
        if review_section:
            rating_span = review_section.find("span", {"class": "a-icon-alt"})
            if rating_span:
                return extract_rating(rating_span.get_text())
        
        return None
    
    def _extract_review_count(self, soup: BeautifulSoup) -> int | None:
        """Extract number of reviews."""
        # Review count link
        review_link = soup.find("span", {"id": "acrCustomerReviewText"})
        if review_link:
            return extract_review_count(review_link.get_text())
        
        # Alternative: ratings count
        ratings_count = soup.find("a", {"id": "acrCustomerReviewLink"})
        if ratings_count:
            return extract_review_count(ratings_count.get_text())
        
        return None
    
    def _extract_seller(self, soup: BeautifulSoup) -> str | None:
        """Extract seller name."""
        # Sold by merchant
        merchant = soup.find("a", {"id": "sellerProfileTriggerId"})
        if merchant:
            return merchant.get_text(strip=True)
        
        # Ships from and sold by
        sold_by = soup.find("div", {"id": "merchant-info"})
        if sold_by:
            text = sold_by.get_text(strip=True)
            if "Amazon" in text:
                return "Amazon"
            return text[:100]  # Truncate long text
        
        return None
    
    def _extract_image(self, soup: BeautifulSoup) -> str | None:
        """Extract main product image URL."""
        # Main image
        img = soup.find("img", {"id": "landingImage"})
        if img and img.get("src"):
            return img["src"]
        
        # Alternative: main image container
        img_container = soup.find("div", {"id": "imgTagWrapperId"})
        if img_container:
            img = img_container.find("img")
            if img and img.get("src"):
                return img["src"]
        
        return None
