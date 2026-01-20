"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Loader2, ExternalLink, RefreshCw, TrendingDown, TrendingUp, Search, Sparkles } from "lucide-react";
import Link from "next/link";
import { Product, fetchProducts, addProduct, triggerScrape, getScrapeStats } from "@/lib/api";
import HowItWorks from "@/components/how-it-works";
import SupportedPlatforms from "@/components/supported-platforms";
import Faq from "@/components/faq";
import Footer from "@/components/footer";

interface ProductWithChange extends Product {
  price_change?: number;
}

export default function Home() {
  const [products, setProducts] = useState<ProductWithChange[]>([]);
  const [url, setUrl] = useState("");
  const [isAdding, setIsAdding] = useState(false);
  const [isFetching, setIsFetching] = useState(true);
  const [scrapeSuccess, setScrapeSuccess] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const loadProducts = async () => {
    try {
      setIsFetching(true);
      const response = await fetchProducts();
      setProducts(response.products.map(p => ({ ...p, price_change: 0 })));
    } catch (err) {
      console.error("Failed to load products:", err);
    } finally {
      setIsFetching(false);
    }
  };

  const loadStats = async () => {
    try {
      const stats = await getScrapeStats();
      setScrapeSuccess(stats.success_rate);
    } catch (err) {
      console.error("Failed to load stats:", err);
    }
  };

  useEffect(() => {
    loadProducts();
    loadStats();
  }, []);

  const formatPrice = (price: number | null, currency: string) => {
    if (price === null) return "—";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency,
    }).format(price);
  };

  const formatTimeAgo = (dateString: string | null) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${Math.floor(diffHours / 24)}d ago`;
  };

  const getPlatformColor = (platform: string) => {
    switch (platform) {
      case "amazon": return "bg-orange-500/10 text-orange-500";
      case "walmart": return "bg-blue-600/10 text-blue-600";
      default: return "bg-gray-500/10 text-gray-500";
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    // Ensure URL has protocol
    let cleanUrl = url.trim();
    if (!cleanUrl.startsWith("http")) {
      cleanUrl = "https://" + cleanUrl;
    }

    setIsAdding(true);
    setError(null);

    try {
      const newProduct = await addProduct(cleanUrl);
      setProducts([{ ...newProduct, price_change: 0 }, ...products]);
      setUrl("");

      // Trigger scrape in background
      try {
        await triggerScrape(newProduct.id);
        loadProducts();
      } catch {
        loadProducts();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add product");
    } finally {
      setIsAdding(false);
    }
  };

  return (
    <main className="min-h-dvh bg-background">


      {/* Hero Section with URL Input */}
      <section className="relative py-16 md:py-24 border-b border-border/40">
        {/* Blue glow background effect */}
        <div className="w-full h-full absolute -top-32 flex justify-end items-center pointer-events-none overflow-hidden">
          <div className="w-3/4 flex justify-center items-center">
            <div className="w-12 h-[600px] bg-light blur-[70px] rounded-3xl max-sm:rotate-15 sm:rotate-35 will-change-transform"></div>
          </div>
        </div>
        <div className="container mx-auto px-4 max-w-3xl text-center">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
            Track product prices on <span className="text-light">Amazon and Walmart.</span>
          </h1>
          <p className="text-lg text-muted-foreground mb-8">
            Paste any Amazon or Walmart product URL to start tracking its price.
          </p>

          {/* URL Input Form */}
          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                placeholder="Paste Amazon or Walmart product URL..."
                className="w-full h-14 pl-12 pr-4 rounded-xl border border-border bg-card text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-light/50 focus:border-light"
              />
            </div>
            <Button
              type="submit"
              disabled={isAdding || !url.trim()}
              className="h-14 px-8 rounded-xl bg-light hover:bg-light/90 text-white font-medium"
            >
              {isAdding ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  Adding...
                </>
              ) : (
                <>
                  <Plus className="w-5 h-5 mr-2" />
                  Track Price
                </>
              )}
            </Button>
          </form>

          {error && (
            <p className="mt-4 text-sm text-red-500">{error}</p>
          )}

          <p className="mt-4 text-sm text-muted-foreground">
            Supports Amazon (all regions) and Walmart
          </p>
        </div>
      </section>

      {/* Products Section */}
      <section className="py-12">
        <div className="container mx-auto px-4">
          {/* Stats Bar */}
          <div className="flex flex-wrap items-center justify-between gap-4 mb-8">
            <div className="flex items-center gap-6">
              <div>
                <span className="text-2xl font-bold">{products.length}</span>
                <span className="text-muted-foreground ml-2">Products</span>
              </div>
              <div>
                <span className="text-2xl font-bold text-light">{scrapeSuccess}%</span>
                <span className="text-muted-foreground ml-2">Success Rate</span>
              </div>
            </div>
            <Button variant="outline" onClick={loadProducts} disabled={isFetching}>
              <RefreshCw className={`w-4 h-4 mr-2 ${isFetching ? "animate-spin" : ""}`} />
              Refresh
            </Button>
          </div>

          {/* Loading State */}
          {isFetching && products.length === 0 && (
            <div className="flex justify-center py-12">
              <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
          )}

          {/* Product Grid */}
          {products.length > 0 && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {products.map((product) => (
                <Card key={product.id} className="hover:border-foreground/20 transition-colors">
                  <CardHeader className="pb-3">
                    <div className="flex items-start justify-between">
                      <span className={`text-xs px-2 py-1 rounded-full font-medium ${getPlatformColor(product.platform)}`}>
                        {product.platform.charAt(0).toUpperCase() + product.platform.slice(1)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {formatTimeAgo(product.last_scraped_at)}
                      </span>
                    </div>
                    <CardTitle className="text-base line-clamp-2 mt-2">
                      {product.name || "Loading..."}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="flex items-baseline justify-between">
                      <div>
                        <span className="text-2xl font-bold">
                          {formatPrice(product.current_price, product.currency)}
                        </span>
                        {product.price_change !== undefined && product.price_change !== 0 && (
                          <span className={`ml-2 text-sm inline-flex items-center ${product.price_change < 0 ? "text-light" : "text-red-500"}`}>
                            {product.price_change < 0 ? <TrendingDown className="w-3 h-3 mr-1" /> : <TrendingUp className="w-3 h-3 mr-1" />}
                            {Math.abs(product.price_change)}%
                          </span>
                        )}
                      </div>
                      {!product.in_stock && (
                        <span className="text-xs bg-red-500/10 text-red-500 px-2 py-1 rounded-full">Out of Stock</span>
                      )}
                    </div>

                    {product.lowest_price && product.highest_price && (
                      <div className="flex justify-between text-sm text-muted-foreground">
                        <span>Low: {formatPrice(product.lowest_price, product.currency)}</span>
                        <span>High: {formatPrice(product.highest_price, product.currency)}</span>
                      </div>
                    )}

                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1" asChild>
                        <Link href={`/products/${product.id}`}>View Details</Link>
                      </Button>
                      <Button variant="outline" size="sm" asChild>
                        <a href={product.url} target="_blank" rel="noopener noreferrer">
                          <ExternalLink className="w-4 h-4" />
                        </a>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}

          {/* Empty State */}
          {!isFetching && products.length === 0 && (
            <div className="text-center py-16">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                <Search className="w-8 h-8 text-muted-foreground" />
              </div>
              <h3 className="text-lg font-medium mb-2">No products tracked yet</h3>
              <p className="text-muted-foreground mb-4">
                Paste a product URL above to start tracking prices
              </p>
            </div>
          )}
        </div>
      </section>

      <div id="how-it-works">
        <HowItWorks />
      </div>
      <div id="platforms">
        <SupportedPlatforms />
      </div>
      <div id="faq">
        <Faq />
      </div>

      <Footer />
    </main>
  );
}
