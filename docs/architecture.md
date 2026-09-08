# AirFareX System Architecture & Design Specification

## 1. Executive Summary

**AirFareX (Indian Airfare Price Index - APIx)** is a prototype platform designed to measure, monitor, and analyze domestic airfare price trends across India in real-time. By leveraging automated airfare data acquisition, statistical normalization, median price aggregation, and a Laspeyres price index framework ($\text{APIX\_v1}$), AirFareX provides policymakers, researchers, statisticians (e.g. NSO, MoSPI, RBI), and quantitative analysts with high-frequency indices capable of augmenting official Consumer Price Index (CPI) transport indicators.

---

## 2. System Architecture

```text
                                +-------------------------------+
                                |  Public / Synthetic Sources   |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |    Provider Adapters Layer    |
                                |  - MockFareProvider           |
                                |  - DatasetFareProvider        |
                                |  - Permitted HTTP Providers   |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |   Data Acquisition Engine     |
                                |  (Scheduler & Pipeline CLI)   |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |  Cleaning & Normalization     |
                                |  - Standardizer & Calculator  |
                                |  - SHA-256 Deduplication      |
                                |  - MAD / IQR Outlier Detector |
                                |  - Data Quality Scoring       |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |  Storage (SQLite/PostgreSQL)  |
                                |  - Raw & Cleaned FareQuotes   |
                                |  - Quality & Run Records      |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |  Index Construction Engine    |
                                |  - Base Period Baseline P_i,0 |
                                |  - Route Index (Laspeyres)    |
                                |  - National APIx Index        |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |  FastAPI REST Services & API  |
                                |  - Fares, Index, Analytics    |
                                |  - Quality & Admin Endpoints  |
                                +---------------+---------------+
                                                |
                                                v
                                +---------------+---------------+
                                |  React Vite Dashboard (UI)    |
                                |  - KPI Cards, Line Charts     |
                                |  - Heatmaps, Lead-time curves |
                                |  - Data Explorer & CSV Export |
                                +-------------------------------+
```

---

## 3. Database Schema

AirFareX uses SQLAlchemy ORM supporting both SQLite for instant zero-dependency execution and PostgreSQL for production deployments.

### 3.1 `routes`
* `id` (INTEGER, PK, Autoincrement)
* `route_code` (VARCHAR(16), Unique, Indexed) e.g., "DEL-BOM"
* `origin` (VARCHAR(3)) e.g., "DEL"
* `destination` (VARCHAR(3)) e.g., "BOM"
* `origin_city` (VARCHAR(64)) e.g., "Delhi"
* `destination_city` (VARCHAR(64)) e.g., "Mumbai"
* `weight` (FLOAT) e.g., 0.18 (`DEMO_WEIGHTS`)
* `active` (BOOLEAN, Default True)
* `created_at` (DATETIME, Default UTC Now)

### 3.2 `carriers`
* `id` (INTEGER, PK, Autoincrement)
* `name` (VARCHAR(64)) e.g., "IndiGo"
* `iata_code` (VARCHAR(3), Unique, Indexed) e.g., "6E"
* `source_type` (VARCHAR(32)) e.g., "LCC" / "FSC"
* `active` (BOOLEAN, Default True)

### 3.3 `fare_quotes`
* `id` (INTEGER, PK, Autoincrement)
* `observation_timestamp` (DATETIME, Indexed)
* `origin` (VARCHAR(3), Indexed)
* `destination` (VARCHAR(3), Indexed)
* `departure_date` (DATE, Indexed)
* `lead_time_days` (INTEGER, Indexed) e.g., 1, 7, 15, 30, 45
* `carrier` (VARCHAR(64))
* `flight_number` (VARCHAR(32))
* `fare_class` (VARCHAR(32)) e.g., "Economy", "Flex"
* `base_fare` (FLOAT)
* `taxes` (FLOAT)
* `airport_fee` (FLOAT)
* `fuel_surcharge` (FLOAT)
* `user_development_fee` (FLOAT)
* `convenience_fee` (FLOAT)
* `other_fee` (FLOAT)
* `total_fare` (FLOAT, Indexed)
* `currency` (VARCHAR(3), Default "INR")
* `source` (VARCHAR(64)) e.g., "mock_provider", "dataset_provider"
* `source_url` (VARCHAR(256), Nullable)
* `availability_status` (VARCHAR(32)) e.g., "AVAILABLE", "LIMITED", "SOLD_OUT"
* `collection_status` (VARCHAR(32)) e.g., "VALID", "REJECTED"
* `raw_hash` (VARCHAR(64), Indexed) SHA-256 fingerprint
* `created_at` (DATETIME, Default UTC Now)

### 3.4 `data_quality_records`
* `id` (INTEGER, PK, Autoincrement)
* `fare_quote_id` (INTEGER, FK -> `fare_quotes.id`, Indexed)
* `quality_score` (FLOAT) e.g., 0.0 - 100.0%
* `missing_fields` (TEXT, JSON-encoded list)
* `outlier_flag` (BOOLEAN, Default False)
* `duplicate_flag` (BOOLEAN, Default False)
* `validation_errors` (TEXT, JSON-encoded list)
* `created_at` (DATETIME, Default UTC Now)

### 3.5 `index_observations`
* `id` (INTEGER, PK, Autoincrement)
* `observation_date` (DATE, Indexed)
* `route_code` (VARCHAR(16), Indexed) e.g., "DEL-BOM" or "NATIONAL"
* `lead_time_bucket` (INTEGER, Indexed) e.g., 1, 7, 15, 30, 45, or 0 (ALL)
* `route_index` (FLOAT) Base = 100.0
* `national_index` (FLOAT) Weighted aggregate
* `base_period` (VARCHAR(64)) e.g., "2026-08-BASE30"
* `weight` (FLOAT) Route weight used
* `sample_count` (INTEGER) Number of fare quotes aggregated
* `methodology_version` (VARCHAR(32)) e.g., "APIX_v1"
* `created_at` (DATETIME, Default UTC Now)

### 3.6 `data_collection_runs`
* `id` (INTEGER, PK, Autoincrement)
* `started_at` (DATETIME)
* `completed_at` (DATETIME, Nullable)
* `source` (VARCHAR(64))
* `routes_requested` (INTEGER)
* `quotes_collected` (INTEGER)
* `quotes_valid` (INTEGER)
* `quotes_rejected` (INTEGER)
* `status` (VARCHAR(32)) e.g., "RUNNING", "COMPLETED", "FAILED"
* `error_summary` (TEXT, Nullable)

---

## 4. Airfare Price Index Methodology ($\text{APIX\_v1}$)

### 4.1 Representative Fare Calculation
Airfare distributions exhibit right-skewness due to premium last-minute fares. Therefore, AirFareX uses the **median total fare** as the central tendency representative price $P_{i,t,l}$ for route $i$, date $t$, and lead-time bucket $l$:

\[
P_{i,t,l} = \text{Median}\left( \{ \text{total\_fare}_{k} \mid k \in \text{Route } i, \text{ Date } t, \text{ LeadTime } l, \text{ Outlier } = \text{False} \} \right)
\]

### 4.2 Route Index Formula
For route $i$ at time $t$ relative to base period price $P_{i,0}$:

\[
I_{i,t} = \left( \frac{P_{i,t}}{P_{i,0}} \right) \times 100
\]

### 4.3 National Airfare Price Index ($\text{APIx}$)
Using normalized route weights $w_i$ ($\sum w_i = 1.0$):

\[
\text{APIx}_t = \frac{\sum_{i=1}^{N} w_i \times I_{i,t}}{\sum_{i=1}^{N} w_i}
\]

---

## 5. REST API Specifications

* `GET /api/health`: Health status & database check.
* `GET /api/routes`: List configured routes and demo weights.
* `GET /api/carriers`: Carrier master list.
* `GET /api/fares`: Search fare quotes (with route, carrier, date, lead-time filters and pagination).
* `GET /api/fares/latest`: Get latest collected fare quotes.
* `GET /api/index`: Get latest APIx national and route indices.
* `GET /api/index/history`: Time series of national and route indices.
* `GET /api/index/route/{route_code}`: Historical index breakdown for specific route.
* `GET /api/analytics/lead-time`: Advance purchase lead-time curves.
* `GET /api/analytics/carriers`: Carrier price comparison & dispersion stats.
* `GET /api/analytics/routes`: Route inflation rates & price volatility metrics.
* `GET /api/data-quality`: Data quality overview, outlier rate, duplicate counts.
* `GET /api/collection-runs`: Collection execution history logs.

---

## 6. Ethical & Legal Scraping Architecture

To maintain strict compliance:
1. **Robots.txt parser**: Checks permissions prior to HTTP requests.
2. **Conservative Rate Limiting**: Enforces minimum 5.0 second delay between requests.
3. **No Evading Security**: Zero CAPTCHA solving, zero header manipulation, zero unauthorized IP proxies.
4. **Demonstrable Fallbacks**: `MockFareProvider` and `DatasetFareProvider` deliver 100% full application functionality when external endpoints are restricted.

---

## 7. TODO Progress Roadmap

- [x] Phase 1: Architecture & Project Initialization
- [ ] Phase 2: Database Schema & SQLAlchemy Models
- [ ] Phase 3: Synthetic Airfare Generator (30 days, 10 routes, 5 lead windows, fixed seed)
- [ ] Phase 4: Data Normalization, Deduplication & Quality Engine
- [ ] Phase 5: Airfare Price Index Calculation Engine (APIX_v1)
- [ ] Phase 6: FastAPI REST API Implementation
- [ ] Phase 7: React Vite Dashboard Development
- [ ] Phase 8: Advanced Analytics & Lead-time elasticity
- [ ] Phase 9: 30-Day Backtesting Engine
- [ ] Phase 10: Provider Abstraction & Ethical Permitted Adapters
- [ ] Phase 11: Dockerization & Container Setup
- [ ] Phase 12: Automated Tests (>70% coverage) & Verification Walkthrough
