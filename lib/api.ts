/**
 * API client for PriceWatch backend.
 * Handles all communication with the FastAPI backend.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ============== Types ==============

export interface Product {
    id: string;
    url: string;
    platform: string;
    name: string | null;
    image_url: string | null;
    current_price: number | null;
    currency: string;
    in_stock: boolean;
    rating: number | null;
    review_count: number | null;
    seller_name: string | null;
    price_alert_threshold: number | null;
    alert_email: string | null;
    lowest_price: number | null;
    highest_price: number | null;
    scrape_frequency_hours: number;
    last_scraped_at: string | null;
    last_alert_sent_at: string | null;
    created_at: string;
    is_active: boolean;
}

export interface ProductListResponse {
    products: Product[];
    total: number;
    page: number;
    page_size: number;
}

export interface PricePoint {
    price: number;
    currency: string;
    in_stock: boolean;
    recorded_at: string;
}

export interface PriceHistoryResponse {
    product_id: string;
    product_name: string | null;
    current_price: number | null;
    lowest_price: number | null;
    highest_price: number | null;
    price_change_30d: number | null;
    history: PricePoint[];
}

export interface ScrapeResponse {
    product_id: string;
    success: boolean;
    name: string | null;
    current_price: number | null;
    in_stock: boolean;
    response_time_ms: number;
    error_message: string | null;
}

export interface ScrapeStats {
    total_scrapes: number;
    successful_scrapes: number;
    failed_scrapes: number;
    blocked_scrapes: number;
    success_rate: number;
    avg_response_time_ms: number;
    platforms: Record<string, { name: string; supported: boolean }>;
}

// ============== API Functions ==============

async function fetchAPI<T>(
    endpoint: string,
    options?: RequestInit
): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options?.headers,
        },
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
}

// ============== Products ==============

export async function fetchProducts(
    page = 1,
    pageSize = 20,
    platform?: string
): Promise<ProductListResponse> {
    const params = new URLSearchParams({
        page: page.toString(),
        page_size: pageSize.toString(),
        active_only: "true",
    });

    if (platform) {
        params.set("platform", platform);
    }

    return fetchAPI<ProductListResponse>(`/products?${params}`);
}

export async function fetchProduct(id: string): Promise<Product> {
    return fetchAPI<Product>(`/products/${id}`);
}

export async function addProduct(
    url: string,
    options?: {
        price_alert_threshold?: number;
        alert_email?: string;
        scrape_frequency_hours?: number;
    }
): Promise<Product> {
    return fetchAPI<Product>("/products", {
        method: "POST",
        body: JSON.stringify({
            url,
            ...options,
        }),
    });
}

export async function updateProduct(
    id: string,
    data: {
        price_alert_threshold?: number | null;
        alert_email?: string | null;
        scrape_frequency_hours?: number;
        is_active?: boolean;
    }
): Promise<Product> {
    return fetchAPI<Product>(`/products/${id}`, {
        method: "PATCH",
        body: JSON.stringify(data),
    });
}

export async function deleteProduct(id: string): Promise<void> {
    await fetch(`${API_BASE_URL}/products/${id}`, {
        method: "DELETE",
    });
}

// ============== Scraping ==============

export async function triggerScrape(productId: string): Promise<ScrapeResponse> {
    return fetchAPI<ScrapeResponse>(`/scrape/${productId}`, {
        method: "POST",
    });
}

export async function getScrapeStats(): Promise<ScrapeStats> {
    return fetchAPI<ScrapeStats>("/scrape/stats");
}

// ============== Price History ==============

export async function fetchPriceHistory(
    productId: string,
    days = 30
): Promise<PriceHistoryResponse> {
    return fetchAPI<PriceHistoryResponse>(
        `/history/${productId}?days=${days}`
    );
}

export async function exportPriceHistory(
    productId: string,
    format: "csv" | "json" = "csv"
): Promise<Blob> {
    const response = await fetch(
        `${API_BASE_URL}/history/${productId}/export?format=${format}`
    );
    return response.blob();
}

// ============== Health ==============

export async function checkHealth(): Promise<{
    status: string;
    database: string;
    thor_data: {
        proxy_configured: boolean;
        web_unlocker_configured: boolean;
    };
}> {
    return fetchAPI("/health");
}
