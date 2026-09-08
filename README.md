# AirFareX — Indian Airfare Price Index (APIx)

> Real-Time Airfare Price Index Platform for India through Automated Web Scraping & Synthetic Data Adapters for Augmentation of the Consumer Price Index (CPI).

---

## Executive Overview

Official transport CPI indicators in India are traditionally derived from periodic manual surveys or static sampling. **AirFareX** introduces a high-frequency, statistically defensible **Airfare Price Index ($\text{APIX\_v1}$)** across major domestic Indian flight corridors (e.g. DEL-BOM, DEL-BLR, BOM-BLR).

Designed for statisticians, economists, researchers, and policy analysts at NSO, MoSPI, and RBI, AirFareX captures dynamic airfare volatility, advance purchase lead-time pricing curves ($T+1, T+7, T+15, T+30, T+45$), and carrier price dispersion.

---

## Universal Multi-Device Access (Mobiles, Tablets, PCs, LAN)

AirFareX is configured for **universal cross-device connectivity**. Any device connected to your local Wi-Fi / LAN network (iPhone, Android phones, iPads, tablets, laptops) can access the live dashboard in real time!

### 1-Click Launchers

- **Universal Python Launcher (All OS & Devices)**:
  ```bash
  py start_app.py
  ```
  *Automatically detects your local Wi-Fi IP address and displays clickable URLs for local & mobile access.*

- **Windows 1-Click Launcher**: Double-click `start_app.bat`
- **macOS / Linux 1-Click Launcher**: Execute `./start_app.sh`

---

## Key Features

1. **Automated & Synthetic Data Acquisition**: Flexible `FareProvider` architecture featuring realistic synthetic generator (`MockFareProvider`), historical CSV dataset loader (`DatasetFareProvider`), and ethical scraper adapters.
2. **Data Cleaning & Normalization**: Reconstructs total fares (Base Fare + Taxes + Fees + Surcharges), deduplicates records via SHA-256 fingerprinting, and detects price outliers using Median Absolute Deviation (MAD) & Interquartile Range (IQR).
3. **Laspeyres Index Construction**: Calculates median route fares and national weighted aggregate indices ($\text{APIX\_v1}$) relative to configurable baseline periods.
4. **Advance Purchase Lead-Time Analysis**: Analyzes price elasticities across advance booking windows ($T+1$ to $T+45$).
5. **Interactive Responsive Dashboard**: Modern dark-themed dashboard built with React, Vite, TypeScript, Tailwind CSS, and Recharts optimized for mobile, tablet, and desktop screens.
6. **REST API**: Fully typed FastAPI backend with OpenAPI documentation (`/docs`).
7. **30-Day Backtesting Engine**: Evaluates index accuracy against reference baselines reporting MAE, RMSE, and MAPE.
8. **100% Ethical & Compliant**: Strictly respects `robots.txt`, rate limits, and site policies without using CAPTCHA bypass or anti-bot evasion.

---

## Core Routes & Advance Purchase Windows

### Core Routes (`config/routes.yaml`)
- `DEL-BOM` (Delhi - Mumbai) — Weight: 0.18
- `DEL-BLR` (Delhi - Bengaluru) — Weight: 0.15
- `BOM-BLR` (Mumbai - Bengaluru) — Weight: 0.13
- `DEL-CCU` (Delhi - Kolkata) — Weight: 0.10
- `BLR-HYD` (Bengaluru - Hyderabad) — Weight: 0.09
- `MAA-DEL` (Chennai - Delhi) — Weight: 0.09
- `CCU-BLR` (Kolkata - Bengaluru) — Weight: 0.08
- `DEL-HYD` (Delhi - Hyderabad) — Weight: 0.07
- `BOM-DEL` (Mumbai - Delhi) — Weight: 0.06
- `BLR-MAA` (Bengaluru - Chennai) — Weight: 0.05

---

## Airline Web Scrapers (Playwright)

AirFareX includes modular asynchronous Playwright scrapers for India's 5 major domestic carriers in `scraper/`:
- **IndiGo** (`scraper/indigo.py`)
- **Air India** (`scraper/air_india.py`)
- **Air India Express** (`scraper/air_india_express.py`)
- **Akasa Air** (`scraper/akasa.py`)
- **SpiceJet** (`scraper/spicejet.py`)

### Running a Single-Airline Scrape
```bash
# Demo mode (synthetic seeder, zero network requests)
py -m scraper.indigo --demo --origin DEL --destination BOM --advance 7
py -m scraper.air_india --demo --origin DEL --destination BOM --advance 7
py -m scraper.air_india_express --demo --origin DEL --destination BOM --advance 7
py -m scraper.akasa --demo --origin DEL --destination BOM --advance 7
py -m scraper.spicejet --demo --origin DEL --destination BOM --advance 7

# Unified runner across all 5 airlines
py scraper/runner.py --airline all --demo --routes DEL-BOM,DEL-BLR --lead-times 1,7,15
```

### Selector Discovery & Reverse Engineering
Selectors were identified by inspecting rendered DOM trees of booking engines:
- **IndiGo**: Card containers `.flight-card` / `[data-testid="flight-card"]`, flight codes `6E-\d{3,4}`, tiers `Saver`, `Flexi Plus`, `Super 6E`.
- **Air India**: Angular/AEM flight components `.flight-card`, `.flight-result-item`, flight codes `AI-\d{3,4}`, tiers `Comfort`, `Comfort Plus`, `Flex`.
- **Air India Express**: Next.js segment tiles `.flight-tile`, `[data-testid="flight-tile"]`, flight codes `IX-\d{3,4}`, tiers `Xpress Lite`, `Xpress Value`, `Xpress Flex`.
- **Akasa Air**: React flight cards `.akasa-flight-card`, `.flightCard`, flight codes `QP-\d{3,4}`, tiers `Saver`, `Flexi`.
- **SpiceJet**: React Native Web containers `[data-testid="flight-card"]`, `.spice-flight-row`, flight codes `SG-\d{3,4}`, tiers `Spicesaver`, `SpiceMax`.

### Known Fragile Points
1. **Dynamic CSS Module Hashes**: Minified class names change across releases (e.g. SpiceJet `css-1dbjc4n`). Mitigated via fallback `data-testid` attributes and flight number regex patterns.
2. **Missing Tax Breakdown**: Search cards often show only total fare. Handled by fallback `cleaning/fare_decomposition.py` heuristics conforming to DGCA and GST rules.
3. **Anti-Bot Screening (Cloudflare, PerimeterX, Kasada)**: Scrapers strictly respect site policies without CAPTCHA bypass; challenge screens trigger graceful skips with logged failure context.
4. **Client Hydration Latency**: Mitigated through Playwright `wait_for_selector` and `networkidle` state synchronization.

For detailed documentation, see [scraper/README.md](scraper/README.md).

---

## Docker One-Command Startup (Multi-Arch AMD64 / ARM64)

```bash
docker compose up --build
```

Access:
- Dashboard UI: `http://localhost:3000`
- REST API: `http://localhost:8000/docs`

