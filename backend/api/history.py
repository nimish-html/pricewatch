"""
Price history API endpoints using Firebase Firestore.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel
import csv
import io
import json

from database import ProductDB, PriceHistoryDB, ScrapeLogDB

router = APIRouter(prefix="/history", tags=["history"])


# ============== Pydantic Schemas ==============

class PricePoint(BaseModel):
    """A single price point in history."""
    price: float
    currency: str
    in_stock: bool
    recorded_at: datetime


class PriceHistoryResponse(BaseModel):
    """Price history for a product."""
    product_id: str
    product_name: Optional[str]
    current_price: Optional[float]
    lowest_price: Optional[float]
    highest_price: Optional[float]
    price_change_30d: Optional[float]
    history: list[PricePoint]


class ScrapeLogEntry(BaseModel):
    """A single scrape log entry."""
    id: str
    status: str
    response_time_ms: Optional[int]
    error_message: Optional[str]
    http_status_code: Optional[int]
    created_at: datetime


class ScrapeLogsResponse(BaseModel):
    """Scrape logs for a product."""
    product_id: str
    logs: list[ScrapeLogEntry]
    total: int


# ============== Endpoints ==============

@router.get("/{product_id}", response_model=PriceHistoryResponse)
async def get_price_history(
    product_id: str,
    days: int = Query(30, ge=1, le=365),
):
    """
    Get price history for a product.
    """
    # Get product
    product = await ProductDB.get_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate date range
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get price history
    history_records = await PriceHistoryDB.get_history(
        product_id=product_id,
        limit=1000,
        since=since,
    )
    
    # Calculate 30-day price change
    price_change_30d = None
    if len(history_records) >= 2:
        oldest_price = history_records[0]["price"]
        newest_price = history_records[-1]["price"]
        if oldest_price and oldest_price > 0:
            price_change_30d = round(
                ((newest_price - oldest_price) / oldest_price) * 100, 2
            )
    
    return PriceHistoryResponse(
        product_id=product_id,
        product_name=product.get("name"),
        current_price=product.get("current_price"),
        lowest_price=product.get("lowest_price"),
        highest_price=product.get("highest_price"),
        price_change_30d=price_change_30d,
        history=[
            PricePoint(
                price=record["price"],
                currency=record["currency"],
                in_stock=record["in_stock"],
                recorded_at=record["recorded_at"],
            )
            for record in history_records
        ],
    )


@router.get("/{product_id}/logs", response_model=ScrapeLogsResponse)
async def get_scrape_logs(
    product_id: str,
    limit: int = Query(50, ge=1, le=200),
):
    """
    Get scrape logs for a product.
    """
    # Check product exists
    product = await ProductDB.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Get logs
    logs = await ScrapeLogDB.get_logs(product_id, limit=limit)
    
    return ScrapeLogsResponse(
        product_id=product_id,
        logs=[
            ScrapeLogEntry(
                id=log["id"],
                status=log["status"],
                response_time_ms=log.get("response_time_ms"),
                error_message=log.get("error_message"),
                http_status_code=log.get("http_status_code"),
                created_at=log["created_at"],
            )
            for log in logs
        ],
        total=len(logs),
    )


@router.get("/{product_id}/export")
async def export_price_history(
    product_id: str,
    format: str = Query("csv", pattern="^(csv|json)$"),
    days: int = Query(365, ge=1, le=365),
):
    """
    Export price history as CSV or JSON.
    """
    # Get product
    product = await ProductDB.get_by_id(product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Calculate date range
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get price history
    history_records = await PriceHistoryDB.get_history(
        product_id=product_id,
        limit=10000,
        since=since,
    )
    
    if format == "csv":
        # Generate CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Date", "Price", "Currency", "In Stock"])
        
        for record in history_records:
            writer.writerow([
                record["recorded_at"].isoformat(),
                record["price"],
                record["currency"],
                "Yes" if record["in_stock"] else "No",
            ])
        
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=price_history_{product_id}.csv"
            }
        )
    
    else:  # JSON
        data = {
            "product_id": product_id,
            "product_name": product.get("name"),
            "product_url": product.get("url"),
            "exported_at": datetime.utcnow().isoformat(),
            "history": [
                {
                    "date": record["recorded_at"].isoformat(),
                    "price": record["price"],
                    "currency": record["currency"],
                    "in_stock": record["in_stock"],
                }
                for record in history_records
            ]
        }
        
        return Response(
            content=json.dumps(data, indent=2),
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=price_history_{product_id}.json"
            }
        )
