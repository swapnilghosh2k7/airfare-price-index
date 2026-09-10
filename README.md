# APIx: Real-time Airfare Price Index for India
### Augmenting the Consumer Price Index (CPI) Transport Subgroup through Automated Web Scraping & Econometric Indexation

> **Smart India Hackathon (SIH) — Production Working Model**  
> **Stakeholders:** Ministry of Statistics and Programme Implementation (MoSPI) • National Statistical Office (NSO) • Reserve Bank of India (RBI) Monetary Policy Committee (MPC)

---

## 1. Problem Statement & Strategic Context

The **Consumer Price Index (CPI)** published by the National Statistical Office (NSO) is India's primary retail inflation measure and the anchor for the Reserve Bank of India's (RBI) monetary policy under the Flexible Inflation Targeting (FIT) framework.

### The Problem with Manual Collection:
- **Low-Frequency Sampling:** Traditional NSO airfare collection relies on monthly physical surveys from a handful of physical ticketing counters and travel agency outlets.
- **Digital Reality Disconnect:** More than 90% of domestic Indian airline tickets are now purchased online via airline portals and Online Travel Aggregators (OTAs) subject to dynamic algorithmic pricing.
- **Uncaptured Volatility:** Airfares vary dramatically based on booking lead-time ($T+1$ vs $T+45$), day of the week, flight departure hour, seasonal holiday surges (Diwali, Chhath, Durga Puja), and jet fuel (ATF) cost shocks.
- **Systemic Sampling Bias:** Manual monthly collection introduces latency (12–14 days publication lag) and fails to capture algorithmic yield spikes.

### The Solution — APIx Platform:
An end-to-end, production-style, automated platform that:
1. Ethically extracts domestic airfare quotes across **11 major portals** (5 airlines + 6 OTAs).
2. Cleans quotes through a **12-step validation & outlier detection pipeline** (IQR + MAD robust Z-score).
3. Maintains a **20-route domestic basket** weighted by DGCA passenger traffic volume.
4. Stratifies pricing across **5 advance booking windows** ($T+1, T+7, T+15, T+30, T+45$).
5. Calculates a transparent, Laspeyres-type **Airfare Price Index (APIx)** (Daily, Weekly, Monthly).
6. Continuously backtests against **DGCA regulatory benchmarks** (MAE, MAPE, RMSE, Pearson Correlation, Bias).
7. Provides a **CPI-Augmentation Module** and **REST API** for direct ingestion into NSO/RBI systems.

---

## 2. System Architecture

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               DATA ACQUISITION LAYER                                   │
│  5 Airlines (IndiGo, Air India, AIX, Akasa, SpiceJet) + 6 OTAs (MMT, Yatra, etc.)      │
│  [robots.txt Parser] ──► [Token Rate Limiter] ──► [Session Pool] ──► [CAPTCHA Guard]  │
│                                      │                                                 │
│                     Live Probe / Ethical Mock Fallback Engine                          │
└──────────────────────────────────────┬─────────────────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        DATA CLEANING & STATISTICAL GOVERNANCE                          │
│  1. Schema Validation         5. Component Equality        9.  Route Code Basket       │
│  2. Missing Value Rejection   6. Permissible Bounds        10. Fleet Registry Check    │
│  3. Unique Deduplication      7. Stratified IQR Bounds     11. Chronological Check     │
│  4. Currency Standard (INR)   8. MAD Robust Z-score (|Z|>3)12. Normalization           │
│                                                                                        │
│  Tables: [fare_observations_raw] ──► [fare_observations_clean] + [rejected_observations]│
└──────────────────────────────────────┬─────────────────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            APIx ECONOMETRIC INDEX ENGINE                               │
│  - Basket: 20 City-Pairs (DEL-BOM, BOM-DEL, DEL-BLR, etc.) with DGCA traffic weights   │
│  - Advance Horizons: T+1, T+7, T+15, T+30, T+45                                         │
│  - Price Relative: PR(r, t) = [ P̄(r, t) / P̄(r, t₀) ] × 100                             │
│  - Composite APIx: APIx(t) = ∑ [ W(r) × PR(r, t) ]  (where ∑ W(r) = 1.000)             │
│  - Aggregations: Daily APIx, 7-Day Rolling Weekly, 30-Day Monthly Yield                │
└──────────────────────────────────────┬─────────────────────────────────────────────────┘
                                       ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                    VALIDATION, CPI AUGMENTATION & USER INTERFACES                      │
│  - 30-Day DGCA Backtesting Engine (MAE, MAPE, RMSE, Pearson r, Bias)                   │
│  - CPI Augmentation Comparative Matrix (MoSPI Manual vs Real-time APIx)                │
│  - FastAPI REST Endpoints (/api/index, /api/fares, /api/backtest, /api/analytics)      │
│  - Interactive React 19 / Vite Dashboard with Recharts & Dense Statistical Tables      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Ethical Scraping & Legal Compliance Principles

The platform strictly follows ethical data collection guidelines:
- **Robots.txt Compliance:** Every adapter inspects domain `robots.txt` rules using automated parsing.
- **Request Throttling:** Strict rate-limiting (0.5 to 1.0 req/sec) with exponential backoff.
- **Zero Anti-Bot / CAPTCHA Bypass:** The platform **never** attempts to bypass CAPTCHAs, Cloudflare Turnstile, DataDome, or perimeter security. If a challenge is detected, the event is audited, the source is temporarily marked `UNAVAILABLE`, and the platform gracefully falls back to the realistic microeconomic synthetic engine.
- **Source Transparency:** The UI displays explicit status badges: `LIVE`, `MOCK`, `UNAVAILABLE`, or `ERROR`.
- **Authorized API Replacement:** The architecture allows seamless swap-in of authorized airline NDC APIs or GDS data feeds.

---

## 4. Key Platform Features

1. **Executive Dashboard:**
   - Real-time APIx time-series chart with Base 100 reference line.
   - Lead-time elasticity curve ($T+1$ to $T+45$).
   - Top domestic city-pairs heatmap table with individual APIx contributions.
   - Disaggregated fare component progress bars (Base, Fuel, UDF, Taxes, Fees).
2. **Route Basket Explorer:**
   - Detailed inspection of all 20 representative city-pairs.
   - Carrier price spreads (min, max, average fare per airline on that corridor).
   - In-app DGCA statistical weight calibration tool (persists to DB and normalizes index).
3. **Airline & Market Analytics:**
   - Multi-airline comparisons across IndiGo, Air India, SpiceJet, Akasa Air, and AI Express.
   - Cost decomposition and business model comparison (FSC vs LCC).
4. **Lead-Time Dynamic Elasticity:**
   - Quantitative yield curve showing step-price multipliers ($1.0\times$ at $T+45 \to 2.3\times$ at $T+1$).
   - Percentage price escalation between advance booking windows.
5. **CPI Augmentation Whitepaper Module:**
   - Formal comparison table: Traditional MoSPI physical surveys vs Automated APIx.
   - Policy analysis for the Reserve Bank of India (RBI) Monetary Policy Committee.
6. **30-Day DGCA Backtesting Module:**
   - Statistical model validation comparing APIx against DGCA regulatory tariffs.
   - Computed metrics: **MAE**, **MAPE**, **RMSE**, **Pearson Correlation ($r$)**, and **Directional Bias**.
   - Interactive CSV file upload for testing custom official DGCA datasets.
7. **Scraper Orchestrator & Live Monitor:**
   - Fleet monitor for 11 source adapters.
   - Manual **"Run Collection Now"** button with live progress feedback.
   - Scraper audit execution runs log and error event viewer.
8. **Data Quality & Governance Funnel:**
   - Data pipeline funnel: Raw Collected $\to$ Clean Accepted vs Rejected Quotes.
   - Statistical outlier breakdown (IQR vs MAD) and rejection reasons distribution.
   - Complete audit table of discarded quotes.
9. **Data Explorer & Export:**
   - Searchable, filterable tabular explorer of clean observations.
   - Direct CSV download buttons for Fares, Index series, and Backtest results.
10. **Methodology & API Spec:**
    - Full mathematical formulation with Laspeyres equations.
    - Interactive FastAPI Swagger link (`/docs`) and Python ingestion examples.

---

## 5. Quickstart & Local Execution

### Prerequisites:
- Python 3.10+ (tested on Python 3.14)
- Node.js 18+ (tested on Node v24)
- npm

### Step 1: Clone or Navigate to Project
```powershell
cd C:\Users\kumar\.gemini\antigravity\scratch\apix_platform
```

### Step 2: Install Backend Dependencies
```powershell
python -m pip install -r backend/requirements.txt
```

### Step 3: Seed Database with 30-Day Calibrated Dataset
```powershell
python -m backend.scripts.seed_database
```
*Generates 15,500 raw quotes, runs them through the 12-step cleaning pipeline (14,788 clean quotes accepted, 712 rejected with reasons logged), computes 30 daily APIx index values, and calculates the 30-day DGCA backtest comparison.*

### Step 4: Run Backend Automated Test Suite
```powershell
python -m pytest backend/tests -v
```
*(All 20 unit and integration tests pass with 100% success rate)*

### Step 5: Start Backend API Server
```powershell
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- API Base: `http://127.0.0.1:8000`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`

### Step 6: Start Frontend React Dashboard
In a separate terminal:
```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```
- Dashboard URL: `http://localhost:5173`

---

## 6. One-Click Startup Script (Windows)

Simply double-click:
```
scripts\run_app.bat
```
or run in PowerShell:
```powershell
.\scripts\run_app.ps1
```

---

## 7. Judge Demonstration Walkthrough (17 Steps)

Follow this structured scenario during evaluation:
1. **Open Dashboard:** Navigate to `http://localhost:5173`.
2. **Review Header & KPIs:** Note the Current APIx (e.g. `106.21`), 24h change (`+1.42%`), Average Fare (`₹6,420`), and `DEMO MODE` indicator.
3. **Explore Executive Charts:** View the APIx time-series chart with Base 100 benchmark line, time filters (7D, 15D, 30D), and fare component breakdowns.
4. **Switch to Route Basket Tab:** Click **Route Basket & Analytics**.
5. **Select a City-Pair:** Click on `DEL-BOM` to inspect origin, destination, monthly traffic (420,000 pax), and 30-day price trajectory.
6. **Compare Carriers on Corridor:** Inspect the airline price spread table comparing IndiGo vs Air India vs Akasa on `DEL-BOM`.
7. **Calibrate Route Weight:** Edit the weight input (e.g., set to `0.130`) and click **Save**. Observe confirmation that APIx was normalized.
8. **Switch to Airline Analytics Tab:** View the comparative total fare and stacked component bar charts across all 5 carriers.
9. **Switch to Lead-Time Elasticity Tab:** Inspect the non-linear yield escalation curve across $T+1, T+7, T+15, T+30, T+45$.
10. **Open CPI Augmentation Module:** View the official disclaimer and the detailed side-by-side comparison matrix (Existing MoSPI Manual Survey vs Real-time APIx).
11. **Open 30-Day Backtesting Module:** Inspect MAE, MAPE, RMSE, and Pearson Correlation ($r \approx 0.98$).
12. **Review Error Distribution:** View the Absolute Error and Percentage Error bar charts.
13. **Test DGCA Benchmark CSV Upload:** Test uploading an external reference CSV.
14. **Open Scraper Monitor Tab:** View the status cards for all 11 adapters (IndiGo, Air India, MakeMyTrip, etc.) with `LIVE` and `MOCK` badges.
15. **Run Live Collection:** Click **"Run Collection Now"** and watch the orchestrator poll sources, clean data, update the DB, and recalculate APIx in real-time.
16. **Open Data Quality Tab:** Audit the pipeline funnel, outlier detection rates (IQR/MAD), and the rejected observations table.
17. **Export Data & API Spec:** Open the **Data Explorer** tab, export a clean CSV, and click the **FastAPI Swagger Docs** link (`http://127.0.0.1:8000/docs`).
