# PriceWatch 🔍💰

**Open-source e-commerce price tracker with 98% success rate** — Built with Python, FastAPI, and residential proxies for reliable anti-bot bypass.

![PriceWatch Dashboard](/public/preview.png)

Track prices across Amazon (all regions) and Walmart. Get notified when prices drop. Learn production-grade web scraping techniques.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## ✨ Features

- **Multi-Platform Support** — Amazon (US, UK, DE, IN, etc.) and Walmart
- **98% Success Rate** — Residential proxies + Web Unlocker fallback
- **Real-Time Tracking** — Add products via URL, get live price updates
- **Price History** — 30-day charts with high/low tracking
- **Email Price Alerts** — Get notified when prices drop below your target
- **Anti-Detection Built-In** — Proxy rotation, randomized delays, session persistence
- **Beautiful Dashboard** — Next.js 15 + shadcn/ui with dark mode
- **Fully Open Source** — Learn from production-grade scraping code

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js 15)                     │
│  ┌──────────────┬──────────────┬─────────────────────────┐  │
│  │ Product List │ Price Charts │ Add Product             │  │
│  └──────────────┴──────────────┴─────────────────────────┘  │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
┌────────────────────────▼────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Scraper Engine (async Python)                       │    │
│  │ • Residential proxy rotation                        │    │
│  │ • Web Unlocker fallback for anti-bot bypass         │    │
│  │ • Retry logic with exponential backoff              │    │
│  └─────────────────────────────────────────────────────┘    │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│                   External Services                          │
│  ┌─────────────┬─────────────┬────────────────────────┐     │
│  │ Thor Data   │ Thor Data   │ Firebase               │     │
│  │ Residential │ Web Unlocker│ Firestore              │     │
│  │ Proxies     │             │                        │     │
│  └─────────────┴─────────────┴────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 18+
- Python 3.11+
- [Thor Data](https://thordata.com) account (for proxies)
- Firebase project (for database)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/pricewatch.git
cd pricewatch

# Frontend
pnpm install

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

**Frontend** (`/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Backend** (`/backend/.env`):
```env
# Firebase
GOOGLE_APPLICATION_CREDENTIALS=./firebase-credentials.json
FIREBASE_PROJECT_ID=your-project-id

# Thor Data Residential Proxies
THOR_PROXY_USERNAME=td-customer-YOUR_USERNAME
THOR_PROXY_PASSWORD=YOUR_PASSWORD

# Thor Data Web Unlocker (optional, for complex sites)
THOR_WEBUNLOCKER_TOKEN=YOUR_TOKEN
```

### 3. Run Locally

```bash
# Terminal 1: Backend
cd backend && source venv/bin/activate
uvicorn main:app --reload

# Terminal 2: Frontend
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) — paste any Amazon or Walmart product URL to start tracking!

---

## 🛡️ Anti-Detection Techniques

This project implements production-grade anti-bot bypass:

| Technique | Description |
|-----------|-------------|
| **Residential Proxies** | Thor Data rotating IPs that appear as real users |
| **Sticky Sessions** | Same IP for 5-10 requests to mimic human browsing |
| **Randomized Delays** | 1-3 second jitter between requests |
| **Web Unlocker Fallback** | Automatic CAPTCHA solving when blocked |
| **Exponential Backoff** | Smart retry logic on failures |
| **Rotating User Agents** | Browser fingerprint randomization |

### Why Residential Proxies?

Datacenter proxies get blocked almost immediately on Amazon/Walmart. Residential proxies route through real ISPs, making requests indistinguishable from normal users.

---

## 📁 Project Structure

```
pricewatch/
├── app/                    # Next.js frontend
│   ├── page.tsx           # Main tracking interface
│   └── products/[id]/     # Product detail pages
├── components/            # React components
├── backend/
│   ├── main.py           # FastAPI entry point
│   ├── api/              # API routes
│   ├── scrapers/         # Platform-specific scrapers
│   │   ├── base.py       # Base scraper with proxy logic
│   │   ├── amazon.py     # Amazon scraper
│   │   └── walmart.py    # Walmart scraper
│   └── database/         # Firebase integration
└── docs/                 # Additional documentation
```

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /products` | GET | List all tracked products |
| `POST /products` | POST | Add new product by URL |
| `GET /products/{id}` | GET | Get product details |
| `POST /scrape/{id}` | POST | Trigger manual scrape |
| `GET /history/{id}` | GET | Get price history |
| `GET /scrape/stats` | GET | Get scraping success stats |

Full API docs available at `/docs` when running locally.

---

## 🧪 Testing

```bash
# Test a single scrape
curl -X POST http://localhost:8000/scrape/PRODUCT_ID

# Check scraping stats
curl http://localhost:8000/scrape/stats
```

---

## 🚢 Deployment

**Frontend:** Deploy to [Vercel](https://vercel.com) with one click.

**Backend:** Deploy to [Fly.io](https://fly.io):
```bash
cd backend
fly launch
fly secrets set THOR_PROXY_USERNAME=xxx THOR_PROXY_PASSWORD=xxx
fly deploy
```

---

## 🤝 Contributing

Contributions welcome! Areas where help is needed:

- [ ] Add Target.com scraper
- [ ] Add eBay scraper
- [x] ~~Add email/Slack price alerts~~ ✅ Done!
- [ ] Add price prediction ML model
- [ ] Add Telegram bot notifications

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📝 License

MIT License — see [LICENSE](license.txt) for details.

---

## 🙏 Acknowledgments

- [Thor Data](https://thordata.com) for residential proxy infrastructure
- [shadcn/ui](https://ui.shadcn.com) for beautiful UI components

---

**Built with ❤️ for the web scraping community**
