"""
Base scraper class with Thor Data proxy integration.
All platform-specific scrapers inherit from this.
"""
from __future__ import annotations

import asyncio
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
import httpx

from config import get_settings
from database.firebase_db import Platform, ScrapeStatus
from .utils import get_random_headers

settings = get_settings()


@dataclass
class ScrapeResult:
    """Result of a scrape operation."""
    
    success: bool
    platform: Platform
    
    # Product data (populated on success)
    name: Optional[str] = None
    current_price: Optional[float] = None
    currency: str = "USD"
    in_stock: bool = True
    image_url: Optional[str] = None
    rating: Optional[float] = None
    review_count: Optional[int] = None
    seller_name: Optional[str] = None
    
    # Scrape metadata
    response_time_ms: int = 0
    status: ScrapeStatus = ScrapeStatus.SUCCESS
    error_message: Optional[str] = None
    http_status_code: Optional[int] = None


class BaseScraper(ABC):
    """
    Abstract base class for e-commerce scrapers.
    
    Features:
    - Thor Data residential proxy integration
    - Thor Data Web Unlocker fallback
    - Randomized headers for anti-detection
    - Retry logic with exponential backoff
    - Request delay jitter
    """
    
    platform: Platform = Platform.UNKNOWN
    
    def __init__(self):
        self.settings = get_settings()
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self, use_proxy: bool = True) -> httpx.AsyncClient:
        """Get or create HTTP client with optional proxy."""
        if self._client is None or self._client.is_closed:
            proxies = None
            if use_proxy and self.settings.thor_proxy_url:
                proxies = {
                    "http://": self.settings.thor_proxy_url,
                    "https://": self.settings.thor_proxy_url,
                }
            
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(self.settings.scrape_timeout_seconds),
                follow_redirects=True,
                proxies=proxies,
            )
        return self._client
    
    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
    
    async def _add_delay(self):
        """Add random delay between requests for human-like timing."""
        delay_ms = random.randint(
            self.settings.scrape_delay_min_ms,
            self.settings.scrape_delay_max_ms
        )
        await asyncio.sleep(delay_ms / 1000)
    
    async def _fetch_with_retry(
        self,
        url: str,
        max_retries: Optional[int] = None,
    ) -> tuple[Optional[str], int, Optional[str]]:
        """
        Fetch URL with retry logic and exponential backoff.
        
        Returns:
            Tuple of (html_content, http_status, error_message)
        """
        max_retries = max_retries or self.settings.scrape_retry_count
        last_error = None
        http_status = 0
        
        for attempt in range(max_retries):
            try:
                await self._add_delay()
                
                client = await self._get_client(use_proxy=True)
                headers = get_random_headers()
                
                response = await client.get(url, headers=headers)
                http_status = response.status_code
                
                if response.status_code == 200:
                    return response.text, http_status, None
                
                # Handle specific error codes
                if response.status_code == 403:
                    last_error = "Access forbidden - likely blocked"
                elif response.status_code == 404:
                    last_error = "Product not found"
                    break  # Don't retry 404s
                elif response.status_code == 503:
                    last_error = "Service unavailable - anti-bot triggered"
                else:
                    last_error = f"HTTP {response.status_code}"
                
            except httpx.TimeoutException:
                last_error = "Request timeout"
            except httpx.ConnectError as e:
                last_error = f"Connection error: {str(e)}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
            
            # Exponential backoff
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                await asyncio.sleep(wait_time)
        
        return None, http_status, last_error
    
    async def _fetch_with_web_unlocker(self, url: str) -> tuple[Optional[str], int, Optional[str]]:
        """
        Fetch URL using Thor Data Web Unlocker for complex anti-bot bypass.
        
        Returns:
            Tuple of (html_content, http_status, error_message)
        """
        if not self.settings.thor_webunlocker_token:
            return None, 0, "Web Unlocker token not configured"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.settings.thor_webunlocker_url,
                    headers={
                        "Authorization": f"Bearer {self.settings.thor_webunlocker_token}",
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                    data={
                        "url": url,
                        "type": "html",
                        "js_render": "True",
                        "header": "False",
                    },
                )
                
                if response.status_code == 200:
                    return response.text, 200, None
                else:
                    return None, response.status_code, f"Web Unlocker returned {response.status_code}"
                    
        except Exception as e:
            return None, 0, f"Web Unlocker error: {str(e)}"
    
    async def scrape(self, url: str) -> ScrapeResult:
        """
        Scrape a product URL.
        
        First attempts with residential proxies.
        Falls back to Web Unlocker if blocked.
        
        Args:
            url: Product URL to scrape
            
        Returns:
            ScrapeResult with product data or error info
        """
        start_time = time.time()
        
        # Try with residential proxies first
        html, http_status, error = await self._fetch_with_retry(url)
        
        # Fallback to Web Unlocker if blocked
        if html is None and http_status in (403, 503, 0):
            html, http_status, error = await self._fetch_with_web_unlocker(url)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        if html is None:
            status = ScrapeStatus.TIMEOUT if "timeout" in (error or "").lower() else ScrapeStatus.FAILED
            if http_status in (403, 503):
                status = ScrapeStatus.BLOCKED
            
            return ScrapeResult(
                success=False,
                platform=self.platform,
                status=status,
                error_message=error,
                http_status_code=http_status,
                response_time_ms=response_time_ms,
            )
        
        # Parse the HTML
        try:
            result = await self.parse(html, url)
            result.response_time_ms = response_time_ms
            result.http_status_code = http_status
            return result
        except Exception as e:
            return ScrapeResult(
                success=False,
                platform=self.platform,
                status=ScrapeStatus.FAILED,
                error_message=f"Parse error: {str(e)}",
                http_status_code=http_status,
                response_time_ms=response_time_ms,
            )
    
    @abstractmethod
    async def parse(self, html: str, url: str) -> ScrapeResult:
        """
        Parse HTML and extract product data.
        
        Args:
            html: Raw HTML content
            url: Original URL (for context)
            
        Returns:
            ScrapeResult with extracted data
        """
        pass
