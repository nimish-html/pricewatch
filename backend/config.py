"""
Configuration settings for PriceWatch backend.
Loads from environment variables with sensible defaults.
"""
from __future__ import annotations

from pydantic_settings import BaseSettings
from functools import lru_cache
import json


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Firebase - use file path (recommended) or inline JSON
    google_application_credentials: str = ""  # File path to service account JSON
    firebase_credentials_json: str = ""  # Or JSON string (single line only)
    firebase_project_id: str = ""
    
    # Thor Data Residential Proxies
    thor_proxy_username: str = ""
    thor_proxy_password: str = ""
    thor_proxy_host: str = "t.pr.thordata.net"
    thor_proxy_port: int = 9999
    
    # Thor Data Web Unlocker
    thor_webunlocker_token: str = ""
    thor_webunlocker_url: str = "https://webunlocker.thordata.com/request"
    
    # Scraping Settings
    scrape_timeout_seconds: int = 30
    scrape_retry_count: int = 3
    scrape_delay_min_ms: int = 1000
    scrape_delay_max_ms: int = 3000
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars like old database_url
    
    @property
    def thor_proxy_url(self) -> str:
        """Build Thor Data residential proxy URL."""
        if not self.thor_proxy_username or not self.thor_proxy_password:
            return ""
        return f"http://{self.thor_proxy_username}:{self.thor_proxy_password}@{self.thor_proxy_host}:{self.thor_proxy_port}"
    
    @property
    def thor_proxy_url_https(self) -> str:
        """Build Thor Data residential proxy URL for HTTPS."""
        if not self.thor_proxy_username or not self.thor_proxy_password:
            return ""
        return f"https://{self.thor_proxy_username}:{self.thor_proxy_password}@{self.thor_proxy_host}:{self.thor_proxy_port}"
    
    def get_firebase_credentials(self) -> dict | None:
        """Parse Firebase credentials from JSON string."""
        if not self.firebase_credentials_json:
            return None
        try:
            return json.loads(self.firebase_credentials_json)
        except json.JSONDecodeError:
            return None


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
