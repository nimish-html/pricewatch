"use client";

import { useState, useEffect, use } from "react";
import { Button } from "@/components/ui/button";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle,
} from "@/components/ui/card";
import {
    Dialog,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import {
    ArrowLeft,
    RefreshCw,
    ExternalLink,
    TrendingDown,
    TrendingUp,
    Download,
    Bell,
    Loader2,
    Trash2,
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Product, fetchProduct, triggerScrape, fetchPriceHistory, exportPriceHistory, deleteProduct, updateProduct, PriceHistoryResponse } from "@/lib/api";

export default function ProductDetailPage({ params }: { params: Promise<{ id: string }> }) {
    const resolvedParams = use(params);
    const router = useRouter();
    const [product, setProduct] = useState<Product | null>(null);
    const [priceHistory, setPriceHistory] = useState<PriceHistoryResponse | null>(null);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [isDeleting, setIsDeleting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Alert Dialog State
    const [isAlertOpen, setIsAlertOpen] = useState(false);
    const [isSavingAlert, setIsSavingAlert] = useState(false);
    const [alertPrice, setAlertPrice] = useState("");
    const [alertEmail, setAlertEmail] = useState("");

    const loadProduct = async () => {
        try {
            setIsLoading(true);
            setError(null);
            const data = await fetchProduct(resolvedParams.id);
            setProduct(data);
            // Initialize alert form
            if (data) {
                setAlertPrice(data.price_alert_threshold?.toString() || "");
                setAlertEmail(data.alert_email || "");
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load product");
        } finally {
            setIsLoading(false);
        }
    };

    const handleSaveAlert = async () => {
        setIsSavingAlert(true);
        try {
            const price = alertPrice ? parseFloat(alertPrice) : null;
            const email = alertEmail || null;

            await updateProduct(resolvedParams.id, {
                price_alert_threshold: price,
                alert_email: email,
            });

            await loadProduct();
            setIsAlertOpen(false);
        } catch (err) {
            console.error("Failed to save alert:", err);
            alert("Failed to save alert settings");
        } finally {
            setIsSavingAlert(false);
        }
    };

    const loadPriceHistory = async () => {
        try {
            const history = await fetchPriceHistory(resolvedParams.id, 30);
            setPriceHistory(history);
        } catch (err) {
            console.error("Failed to load price history:", err);
        }
    };

    // eslint-disable-next-line react-hooks/exhaustive-deps
    useEffect(() => {
        loadProduct();
        loadPriceHistory();
    }, [resolvedParams.id]);

    const formatPrice = (price: number | null, currency: string) => {
        if (price === null) return "—";
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency,
        }).format(price);
    };

    const handleRefresh = async () => {
        setIsRefreshing(true);
        try {
            await triggerScrape(resolvedParams.id);
            await loadProduct();
            await loadPriceHistory();
        } catch (err) {
            console.error("Failed to refresh:", err);
        } finally {
            setIsRefreshing(false);
        }
    };

    const handleDelete = async () => {
        if (!confirm("Are you sure you want to delete this product?")) return;
        setIsDeleting(true);
        try {
            await deleteProduct(resolvedParams.id);
            router.push("/dashboard");
        } catch (err) {
            console.error("Failed to delete:", err);
        } finally {
            setIsDeleting(false);
        }
    };

    const handleExportCSV = async () => {
        try {
            const blob = await exportPriceHistory(resolvedParams.id, "csv");
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = `price_history_${resolvedParams.id}.csv`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Failed to export:", err);
        }
    };

    if (isLoading) {
        return (
            <div className="flex justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
            </div>
        );
    }

    if (error || !product) {
        return (
            <div className="space-y-4">
                <Button variant="ghost" size="icon" asChild>
                    <Link href="/dashboard">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                </Button>
                <Card className="p-12 text-center">
                    <p className="text-red-500 mb-4">{error || "Product not found"}</p>
                    <Button asChild>
                        <Link href="/dashboard">Back to Dashboard</Link>
                    </Button>
                </Card>
            </div>
        );
    }

    const priceChange =
        product.highest_price && product.highest_price > 0 && product.current_price
            ? (((product.current_price - product.highest_price) / product.highest_price) * 100).toFixed(1)
            : "0";

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" asChild>
                    <Link href="/dashboard">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                </Button>
                <div className="flex-1">
                    <h1 className="text-xl font-semibold tracking-tight line-clamp-1">
                        {product.name || "Unknown Product"}
                    </h1>
                    <p className="text-sm text-muted-foreground flex items-center gap-2">
                        <span
                            className={`px-2 py-0.5 rounded-full text-xs font-medium ${product.platform === "amazon"
                                ? "bg-orange-500/10 text-orange-500"
                                : "bg-blue-600/10 text-blue-600"
                                }`}
                        >
                            {product.platform.charAt(0).toUpperCase() + product.platform.slice(1)}
                        </span>
                        <span>•</span>
                        <span>Tracking since {new Date(product.created_at).toLocaleDateString()}</span>
                    </p>
                </div>
                <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handleRefresh} disabled={isRefreshing}>
                        {isRefreshing ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <RefreshCw className="w-4 h-4" />
                        )}
                    </Button>
                    <Button variant="outline" size="sm" asChild>
                        <a href={product.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="w-4 h-4" />
                        </a>
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleDelete} disabled={isDeleting}>
                        {isDeleting ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                        ) : (
                            <Trash2 className="w-4 h-4 text-red-500" />
                        )}
                    </Button>
                </div>
            </div>

            {/* Price Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="md:col-span-2">
                    <CardHeader>
                        <CardTitle className="text-base">Current Price</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="flex items-baseline gap-4">
                            <span className="text-4xl font-bold">
                                {formatPrice(product.current_price, product.currency)}
                            </span>
                            {product.highest_price && product.current_price && (
                                <span
                                    className={`flex items-center text-lg ${parseFloat(priceChange) < 0
                                        ? "text-emerald-500"
                                        : parseFloat(priceChange) > 0
                                            ? "text-red-500"
                                            : "text-muted-foreground"
                                        }`}
                                >
                                    {parseFloat(priceChange) < 0 ? (
                                        <TrendingDown className="w-5 h-5 mr-1" />
                                    ) : parseFloat(priceChange) > 0 ? (
                                        <TrendingUp className="w-5 h-5 mr-1" />
                                    ) : null}
                                    {priceChange}% from high
                                </span>
                            )}
                        </div>
                        <div className="mt-4 grid grid-cols-3 gap-4">
                            <div>
                                <p className="text-sm text-muted-foreground">Lowest</p>
                                <p className="text-lg font-semibold text-emerald-500">
                                    {formatPrice(product.lowest_price, product.currency)}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Average</p>
                                <p className="text-lg font-semibold">
                                    {product.lowest_price && product.highest_price
                                        ? formatPrice(
                                            (product.lowest_price + product.highest_price) / 2,
                                            product.currency
                                        )
                                        : "—"}
                                </p>
                            </div>
                            <div>
                                <p className="text-sm text-muted-foreground">Highest</p>
                                <p className="text-lg font-semibold text-red-500">
                                    {formatPrice(product.highest_price, product.currency)}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <CardTitle className="text-base">Product Info</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-3 text-sm">
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Availability</span>
                            <span className={product.in_stock ? "text-emerald-500" : "text-red-500"}>
                                {product.in_stock ? "In Stock" : "Out of Stock"}
                            </span>
                        </div>
                        {product.rating && (
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Rating</span>
                                <span>{product.rating} ⭐ ({(product.review_count ?? 0).toLocaleString()})</span>
                            </div>
                        )}
                        {product.seller_name && (
                            <div className="flex justify-between">
                                <span className="text-muted-foreground">Seller</span>
                                <span>{product.seller_name}</span>
                            </div>
                        )}
                        <div className="flex justify-between">
                            <span className="text-muted-foreground">Update Frequency</span>
                            <span>Every {product.scrape_frequency_hours}h</span>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Price Chart */}
            <Card>
                <CardHeader className="flex flex-row items-center justify-between">
                    <div>
                        <CardTitle className="text-base">Price History</CardTitle>
                        <CardDescription>Last 30 days</CardDescription>
                    </div>
                    <Button variant="outline" size="sm" onClick={handleExportCSV}>
                        <Download className="w-4 h-4 mr-2" />
                        Export CSV
                    </Button>
                </CardHeader>
                <CardContent>
                    {priceHistory && priceHistory.history.length > 0 ? (
                        <div className="space-y-2">
                            <div className="h-48 flex items-end gap-1 px-4">
                                {priceHistory.history.slice(-30).map((point, i) => {
                                    const maxPrice = Math.max(...priceHistory.history.map(p => p.price));
                                    const minPrice = Math.min(...priceHistory.history.map(p => p.price));
                                    const range = maxPrice - minPrice || 1;
                                    const height = ((point.price - minPrice) / range) * 100;
                                    return (
                                        <div key={i} className="flex-1 flex flex-col items-center gap-1 group relative">
                                            {/* Tooltip on hover */}
                                            <div className="absolute bottom-full mb-2 hidden group-hover:block bg-popover border border-border rounded-lg px-3 py-2 shadow-lg z-10 whitespace-nowrap">
                                                <p className="text-sm font-semibold">{formatPrice(point.price, product.currency)}</p>
                                                <p className="text-xs text-muted-foreground">{new Date(point.recorded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</p>
                                            </div>
                                            <div
                                                className="w-full bg-emerald-500/50 hover:bg-emerald-500 transition-colors rounded-t cursor-pointer"
                                                style={{ height: `${Math.max(height * 1.5, 8)}px` }}
                                            />
                                        </div>
                                    );
                                })}
                            </div>
                            {/* Date labels - show every 5th date for readability */}
                            <div className="flex gap-1 px-4 text-[10px] text-muted-foreground">
                                {priceHistory.history.slice(-30).map((point, i) => (
                                    <div key={i} className="flex-1 text-center">
                                        {i % 7 === 0 ? new Date(point.recorded_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : ''}
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <div className="h-64 bg-muted/30 rounded-lg flex items-center justify-center">
                            <div className="text-center text-muted-foreground">
                                <p>No price history yet</p>
                                <p className="text-sm">Prices will appear after scraping</p>
                            </div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Price Alert */}
            <Card>
                <CardHeader>
                    <div className="flex items-center gap-2">
                        <Bell className="w-5 h-5 text-amber-500" />
                        <CardTitle className="text-base">Price Alert</CardTitle>
                    </div>
                    <CardDescription>
                        Get notified when the price drops below your target
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="flex items-center gap-4">
                        <div className="flex-1">
                            <p className="text-sm text-muted-foreground mb-1">Alert Price</p>
                            <div className="flex items-center gap-2">
                                <span className="text-lg font-semibold">
                                    {product.price_alert_threshold
                                        ? formatPrice(product.price_alert_threshold, product.currency)
                                        : "Not set"}
                                </span>
                                {product.price_alert_threshold && product.current_price && product.current_price <= product.price_alert_threshold ? (
                                    <span className="text-xs bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded-full">
                                        🎉 Below target!
                                    </span>
                                ) : product.price_alert_threshold && product.current_price ? (
                                    <span className="text-xs text-muted-foreground">
                                        {formatPrice(
                                            product.current_price - product.price_alert_threshold,
                                            product.currency
                                        )}{" "}
                                        above target
                                    </span>
                                ) : null}
                            </div>
                            {product.alert_email && (
                                <p className="text-xs text-muted-foreground mt-1">
                                    Alerts sent to: <span className="font-medium">{product.alert_email}</span>
                                </p>
                            )}
                        </div>
                        <Dialog open={isAlertOpen} onOpenChange={setIsAlertOpen}>
                            <DialogTrigger asChild>
                                <Button variant="outline" size="sm">
                                    {product.price_alert_threshold ? "Edit Alert" : "Set Alert"}
                                </Button>
                            </DialogTrigger>
                            <DialogContent>
                                <DialogHeader>
                                    <DialogTitle>Set Price Alert</DialogTitle>
                                    <CardDescription>
                                        We&apos;ll notify you when the price drops below your target.
                                    </CardDescription>
                                </DialogHeader>
                                <div className="space-y-4 py-4">
                                    <div className="space-y-2">
                                        <label htmlFor="price" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Target Price ({product.currency})</label>
                                        <input
                                            id="price"
                                            type="number"
                                            step="0.01"
                                            value={alertPrice}
                                            onChange={(e) => setAlertPrice(e.target.value)}
                                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                            placeholder="Example: 25.00"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label htmlFor="email" className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">Email Address</label>
                                        <input
                                            id="email"
                                            type="email"
                                            value={alertEmail}
                                            onChange={(e) => setAlertEmail(e.target.value)}
                                            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
                                            placeholder="you@example.com"
                                        />
                                        <p className="text-xs text-muted-foreground">
                                            We&apos;ll only email you when a meaningful price drop occurs.
                                        </p>
                                    </div>
                                </div>
                                <DialogFooter>
                                    <Button variant="outline" onClick={() => setIsAlertOpen(false)}>Cancel</Button>
                                    <Button onClick={handleSaveAlert} disabled={isSavingAlert}>
                                        {isSavingAlert && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                                        Save Alert
                                    </Button>
                                </DialogFooter>
                            </DialogContent>
                        </Dialog>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}
