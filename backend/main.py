"""
PriceWatch - E-commerce Price Tracker Backend

FastAPI application entry point with Firebase Firestore integration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_firebase
from api import products_router, scrape_router, history_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    - Initialize Firebase on startup
    - Clean up on shutdown
    """
    # Startup
    init_firebase()
    print("✓ Firebase initialized")
    
    yield
    
    # Shutdown
    print("✓ Shutting down...")


# Create FastAPI app
app = FastAPI(
    title="PriceWatch API",
    description="Open-source e-commerce price tracking with Thor Data proxy integration",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(products_router)
app.include_router(scrape_router)
app.include_router(history_router)


# ============== Health Check ==============

@app.get("/", tags=["health"])
async def root():
    """Root endpoint with API info."""
    return {
        "name": "PriceWatch API",
        "version": "0.1.0",
        "status": "running",
        "database": "firebase",
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "database": "firebase",
        "thor_data": {
            "proxy_configured": bool(settings.thor_proxy_username),
            "web_unlocker_configured": bool(settings.thor_webunlocker_token),
        }
    }


# ============== Run with uvicorn ==============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
