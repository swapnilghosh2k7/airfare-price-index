# AirFareX — Airline Web Scrapers Guide

Comprehensive documentation for the asynchronous Playwright scrapers covering India's five major domestic commercial airlines:
1. **IndiGo** (`goindigo.in`) — `scraper/indigo.py`
2. **Air India** (`airindia.com`) — `scraper/air_india.py`
3. **Air India Express** (`airindiaexpress.com`) — `scraper/air_india_express.py`
4. **Akasa Air** (`akasaair.com`) — `scraper/akasa.py`
5. **SpiceJet** (`spicejet.com`) — `scraper/spicejet.py`

---

## 1. Quick Start: How to Run Scrapers

### Running a Single-Airline Scrape

Each airline scraper is an independent, runnable module inheriting from `scraper/common/base_scraper.py`.

#### IndiGo (`goindigo.in`)
```bash
# Demo mode (synthetic seeder, zero network requests)
py -m scraper.indigo --demo --origin DEL --destination BOM --advance 7

# Live Playwright scrape (headless)
py -m scraper.indigo --origin DEL --destination BOM --advance 7

# Live Playwright scrape (visible browser window for debugging)
py -m scraper.indigo --origin DEL --destination BOM --advance 7 --headless=False
```

#### Air India (`airindia.com`)
```bash
py -m scraper.air_india --demo --origin DEL --destination BOM --advance 7
```

#### Air India Express (`airindiaexpress.com`)
```bash
py -m scraper.air_india_express --demo --origin DEL --destination BOM --advance 7
```

#### Akasa Air (`akasaair.com`)
```bash
py -m scraper.akasa --demo --origin DEL --destination BOM --advance 7
```

#### SpiceJet (`spicejet.com`)
```bash
py -m scraper.spicejet --demo --origin DEL --destination BOM --advance 7
```

---

### Running via the Unified CLI Runner (`scraper/runner.py`)

Run specific airlines, specific routes, and advance windows, or all 5 carriers at once:

```bash
# Run all 5 airlines in demo mode across DEL-BOM for T+1, T+7
py scraper/runner.py --airline all --demo --routes DEL-BOM --lead-times 1,7

# Run only IndiGo and SpiceJet on multiple routes
py scraper/runner.py --airline indigo --demo --routes DEL-BOM,DEL-BLR --lead-times 7,15

# Run in live mode across all configured routes in config/routes.yaml
py scraper/runner.py --airline akasa
```

---

## 2. Architecture & Compliance

```
scraper/
├── common/
│   ├── base_scraper.py       # Async Playwright base class, DB persistence, CAPTCHA detector
│   ├── rate_limiter.py       # Domain-specific async rate limiting (2-4s delay + jitter)
│   └── robots_check.py       # robots.txt parser and per-domain cache
├── config/
│   ├── routes.yaml           # Core monitored domestic flight corridors (DEL-BOM, DEL-BLR, etc.)
│   └── advance_windows.yaml  # Advance purchase windows (T+1, T+7, T+15, T+30, T+45)
├── indigo.py                 # IndiGo carrier scraper
├── air_india.py              # Air India carrier scraper
├── air_india_express.py      # Air India Express carrier scraper
├── akasa.py                  # Akasa Air carrier scraper
├── spicejet.py               # SpiceJet carrier scraper
└── runner.py                 # Multi-carrier CLI orchestrator
```

### Ethical Scraping & Bot Policies
- **`robots.txt` Verification**: Checked via `scraper/common/robots_check.py` before hitting any domain. If forbidden, the search is skipped and logged.
- **Rate Limiting**: Enforced via `scraper/common/rate_limiter.py` with randomized jitter (2.0s - 4.0s) between consecutive queries.
- **Zero Bot Evasion**: Never attempts to bypass or solve CAPTCHAs (Cloudflare, PerimeterX, Kasada, reCAPTCHA). If a challenge or block page is encountered, it logs context and moves to the next route query.
- **Database Tagging**: Every stored quote in `database/models.py` `FareQuote` is tagged with `source="<airline>"` and `source_type="airline_direct"`.

---

## 3. How Selectors Were Found & Reverse-Engineered

Modern airline booking widgets are heavy Single-Page Applications (SPAs) built with React, Angular, or Next.js. Selectors were identified through deep DOM inspection of live search results:

### 1. IndiGo (`goindigo.in`)
- **Booking Flow**: Form parameters submit to `/booking/flight-select.html`.
- **Card Containers**: Rendered with `.flight-card`, `.flight-item`, or `div[data-testid="flight-card"]`.
- **Flight Number**: Found in text labels matching regex `6E[- ]?\d{3,4}` or `.flight-number`.
- **Fare Categories**: Grouped in family cards (`Saver`, `Flexi Plus`, `Super 6E`).
- **Urgency / Seats Left**: Rendered in pill badges matching `\d+\s*(?:seats?\s*)?(?:left|remaining)`.
- **Sold Out**: Identified by `.fare-sold-out` or `:text("Sold Out")`.

### 2. Air India (`airindia.com`)
- **Booking Flow**: Angular / Adobe Experience Manager SPA at `/in/en/book/flight-search.html`.
- **Card Containers**: Matched via `.flight-card`, `.flight-result-item`, or `mat-card`.
- **Flight Number**: Extracted via `AI[- ]?\d{3,4}`.
- **Fare Categories**: Branded tiers (`Comfort`, `Comfort Plus`, `Flex`).
- **Sold Out**: Rendered via `.not-available` or `:text("Sold Out")`.

### 3. Air India Express (`airindiaexpress.com`)
- **Booking Flow**: Next.js SPA at `/search?origin=...&dest=...`.
- **Card Containers**: Segment tiles `.flight-tile`, `.fare-row`, or `[data-testid="flight-tile"]`.
- **Flight Number**: `IX[- ]?\d{3,4}`.
- **Fare Categories**: `Xpress Lite` (hand baggage only), `Xpress Value`, `Xpress Flex`.

### 4. Akasa Air (`akasaair.com`)
- **Booking Flow**: React-based portal at `/booking`.
- **Card Containers**: `.akasa-flight-card`, `.flightCard`, or `[data-testid="flight-card"]`.
- **Flight Number**: `QP[- ]?\d{3,4}`.
- **Fare Categories**: `Saver`, `Flexi`.

### 5. SpiceJet (`spicejet.com`)
- **Booking Flow**: React Native Web application with dynamically generated class hashes (`css-1dbjc4n`, `r-14lw9ot`).
- **Card Containers**: `.spice-flight-row`, `[data-testid="flight-card"]`, or flex containers with testids.
- **Flight Number**: `SG[- ]?\d{3,4}`.
- **Fare Categories**: `Spicesaver`, `SpiceMax`.

---

## 4. Known Fragile Points & Mitigation Strategies

Web scraping live commercial airline engines has several inherent points of failure. The scrapers are built defensively to handle each gracefully:

| Fragile Point | Why It Breaks | Mitigation Implemented |
|---|---|---|
| **Dynamic CSS Module Hashes** (e.g. SpiceJet's `r-14lw9ot`) | Frontend builds regenerate class names on every deployment. | Multi-layered fallback selectors: `data-testid`, semantic tag hierarchy, and regex patterns on flight codes (`6E-`, `AI-`, `IX-`, `QP-`, `SG-`). |
| **Client-Side Hydration Latency** | DOM elements render empty shells before API requests populate prices. | Playwright `wait_for_selector` with polite timeouts (7s) + `networkidle` lifecycle wait. |
| **All-Inclusive Fare Display (Missing Tax Breakdown)** | Airlines frequently show only the total price on search cards without itemizing base fare, GST, and UDF. | Integrated DGCA-compliant **`cleaning/fare_decomposition.py`** heuristic fallback which reconstructs exact base fare, taxes (5% GST), fuel surcharge (YQ), and statutory airport fees. |
| **WAF & Anti-Bot Screening (Cloudflare, PerimeterX, Kasada)** | Periodic IP reputation challenges or JS execution checks block headless browsers. | `detect_captcha_or_block()` scans for challenge phrases and Turnstile/reCAPTCHA badges, logs the blocking event, and continues without hanging or attempting unauthorized bypass. |
| **Date Format Incompatibilities** | Different airlines require different date parameters (Air India requires `DD-MM-YYYY`, IndiGo requires `YYYY-MM-DD`). | Each scraper subclass formats the departure date strictly according to the carrier's URL/POST schema. |
| **Network Outages & Transient Timeouts** | Airport Wi-Fi or transient ISP lag can timeout individual queries. | `run_query` catches `TimeoutError` and general exceptions per query so one failure never aborts the overall pipeline. |

---

## 5. Offline Testing & CI

Tests run 100% offline without network connections or live browsers using saved HTML fixtures in `tests/fixtures/`:

```bash
# Run scraper tests
py -m pytest tests/test_scrapers.py -v

# Run all project tests (backend + scrapers)
py -m pytest backend/tests tests/test_scrapers.py -v
```
