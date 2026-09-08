You are building a working software prototype called APIx (Airfare Price Index)

for an Indian government hackathon (Smart India Hackathon style, NSO/MoSPI/RBI

problem statement). Judges will run this live in a browser. It must actually work,

not just look good.



CONTEXT

The current Indian CPI collects airfare prices manually and misses dynamic,

route-specific, time-sensitive pricing. We are building an automated pipeline that:

1\. Collects airfare quotes from Indian airlines and OTAs (or realistic synthetic

&#x20;  data standing in for them — see DEMO MODE below)

2\. Cleans and normalises the quotes

3\. Constructs a daily/weekly/monthly Airfare Price Index (APIx) using a

&#x20;  DGCA-traffic-weighted basket of city-pairs across multiple advance-purchase

&#x20;  windows

4\. Serves the index and raw analytics via a REST API

5\. Visualises everything on an interactive web dashboard



REPOSITORY STRUCTURE — create exactly this skeleton, do not deviate, because

6 people are working in parallel on frozen interfaces:



airfare-price-index/

├── README.md                     # project overview, setup, run instructions

├── docker-compose.yml            # spins up db + api + dashboard together

├── .env.example

├── .github/workflows/

│   ├── ci.yml                    # lint + test on every push

│   └── scheduled\_scrape.yml      # cron job for daily scraping (can be disabled)

├── docs/

│   ├── architecture.md

│   ├── methodology.md            # index formula, weights, PSD basket design

│   ├── data\_dictionary.md

│   ├── demo\_script.md            # exact steps to demo to judges

│   └── backtest\_report.md

├── scraper/

│   ├── airlines/                 # indigo.py, air\_india.py, akasa.py, spicejet.py,

│   │                              # air\_india\_express.py

│   ├── otas/                     # makemytrip.py, yatra.py, easemytrip.py,

│   │                              # cleartrip.py, ixigo.py, goibibo.py

│   ├── common/

│   │   ├── base\_scraper.py       # abstract base class ALL scrapers inherit

│   │   ├── proxy\_manager.py

│   │   ├── rate\_limiter.py

│   │   └── robots\_check.py       # verifies robots.txt before every scrape

│   ├── config/

│   │   ├── routes.yaml           # basket of city-pairs + weights

│   │   └── advance\_windows.yaml  # T+1, T+7, T+15, T+30, T+45

│   ├── scheduler.py               # orchestrates daily runs across all sources

│   ├── requirements.txt

│   └── README.md

├── cleaning/

│   ├── pipeline.py                # orchestrates the full cleaning DAG

│   ├── outlier\_detection.py       # IQR / z-score / route-specific bounds

│   ├── fare\_decomposition.py      # base fare vs tax vs UDF vs convenience fee

│   ├── deduplication.py

│   ├── missing\_value\_handler.py   # sold-out / cancelled flight handling

│   ├── tests/

│   └── README.md

├── database/

│   ├── schema.sql

│   ├── models.py                  # SQLAlchemy ORM, single source of truth

│   ├── migrations/

│   └── seed\_mock\_data.py          # generates realistic synthetic quotes for DEMO MODE

├── index/

│   ├── apix\_calculator.py         # core index construction module

│   ├── weights.py                 # DGCA-passenger-traffic-based route weights

│   ├── methodology.py             # Laspeyres / Paasche / Fisher / Divisia — pick

│   │                              # one as default (Laspeyres, fixed basket, matches

│   │                              # CPI convention) but keep others pluggable

│   ├── lead\_time\_elasticity.py

│   ├── backtest.py                # compares APIx vs public DGCA monthly avg fares

│   ├── tests/

│   └── README.md

├── api/

│   ├── main.py                    # FastAPI app

│   ├── routers/

│   │   ├── index\_router.py        # /api/v1/index/daily, /weekly, /monthly

│   │   ├── routes\_router.py       # /api/v1/routes, /api/v1/routes/{sector}

│   │   ├── fares\_router.py        # /api/v1/fares/raw

│   │   └── health\_router.py

│   ├── schemas.py                 # Pydantic response models

│   ├── auth.py                    # simple API-key auth for NSO/RBI consumers

│   ├── tests/

│   └── README.md

├── dashboard/

│   ├── (React + Vite + Tailwind + Recharts, OR Streamlit — team's choice,

│   │   see Section 7 for both options)

│   ├── README.md

└── data/

&#x20;   ├── raw/                        # gitignored, scraped output lands here

&#x20;   ├── processed/                  # gitignored, cleaned output lands here

&#x20;   ├── mock/                       # COMMITTED — synthetic demo dataset, \~30-45

&#x20;   │                              # days, so judges can run everything offline

&#x20;   └── dgca\_reference/             # COMMITTED — publicly available DGCA monthly

&#x20;                                    # average domestic fare data, for backtesting



FROZEN INTERFACES (do not change these once set — everyone depends on them)



1\. Every scraper (airline or OTA) implements this contract and writes rows

&#x20;  matching this schema, regardless of source:

&#x20;  {

&#x20;    "source": str,              # "indigo" | "makemytrip" | ...

&#x20;    "source\_type": str,         # "airline\_direct" | "ota"

&#x20;    "origin": str,               # IATA code, e.g. "DEL"

&#x20;    "destination": str,          # IATA code, e.g. "BOM"

&#x20;    "carrier": str,              # operating airline IATA code

&#x20;    "flight\_number": str | null,

&#x20;    "query\_date": date,          # date the scrape ran

&#x20;    "travel\_date": date,

&#x20;    "advance\_purchase\_days": int,   # T+1, T+7, T+15, T+30, T+45

&#x20;    "fare\_class": str,           # economy | premium\_economy | business

&#x20;    "base\_fare\_inr": float,

&#x20;    "taxes\_inr": float,

&#x20;    "udf\_inr": float,

&#x20;    "convenience\_fee\_inr": float,

&#x20;    "total\_fare\_inr": float,

&#x20;    "seats\_available": int | null,

&#x20;    "is\_sold\_out": bool,

&#x20;    "scrape\_timestamp": datetime

&#x20;  }



2\. `database/models.py` defines a single `FareQuote` SQLAlchemy model matching

&#x20;  the schema above, plus a `derived` table `DailyRouteFare` (aggregated,

&#x20;  post-cleaning, one row per route+advance\_window+day) that the index module

&#x20;  reads from. Scraper and cleaning modules must write to a Postgres instance

&#x20;  (or SQLite for local dev) using this model — do not invent a second schema.



3\. `index/apix\_calculator.py` exposes:

&#x20;    compute\_index(frequency: "daily"|"weekly"|"monthly", as\_of: date) -> IndexResult

&#x20;  where IndexResult includes the composite index value, base\_period=100,

&#x20;  per-route sub-indices, and per-advance-window sub-indices.



4\. `api/main.py` is the ONLY thing the dashboard calls. The dashboard never

&#x20;  talks to the database directly. Endpoints:

&#x20;    GET /api/v1/index/{frequency}

&#x20;    GET /api/v1/index/{frequency}/routes/{sector}

&#x20;    GET /api/v1/elasticity/{sector}

&#x20;    GET /api/v1/heatmap

&#x20;    GET /api/v1/backtest

&#x20;    GET /api/v1/health



DEMO MODE (critical — read Section 8 of the full document too)

Add a `DEMO\_MODE=true` environment variable. When true:

&#x20; - scraper/scheduler.py skips live scraping and instead calls

&#x20;   database/seed\_mock\_data.py, which generates statistically realistic fake

&#x20;   quotes (dynamic pricing curve by advance-purchase window, day-of-week and

&#x20;   festival-season multipliers, occasional sold-out flights, 200-400%

&#x20;   intraday variance) for the last 45 days across the full route basket.

&#x20; - Everything downstream (cleaning, index, api, dashboard) runs identically

&#x20;   on this data as it would on real scraped data.

This guarantees the whole pipeline runs end-to-end offline, with no dependency

on live websites being reachable, un-CAPTCHA'd, or ToS-compliant, at demo time.



SCRAPING ETHICS (non-negotiable, code it in, don't just document it)

&#x20; - robots\_check.py must fetch and parse robots.txt for each target domain

&#x20;   before scraping it, and the scraper must abort/skip if disallowed.

&#x20; - rate\_limiter.py enforces a minimum delay per domain (configurable,

&#x20;   default 1 request per 3-5 seconds per source) and randomised jitter.

&#x20; - Do not write code whose purpose is defeating CAPTCHAs or bot-detection.

&#x20;   Where a site blocks automated access, the scraper should log this and

&#x20;   fall back gracefully (skip that source, or use DEMO MODE data), not try

&#x20;   to circumvent the block.

&#x20; - Prefer, where they exist, official/partner data feeds (airline GDS feeds,

&#x20;   aggregator affiliate APIs) over scraping; document this trade-off in

&#x20;   scraper/README.md.



TECH STACK

&#x20; - Python 3.11+, Playwright for JS-rendered pages, Scrapy for simpler pages

&#x20; - Postgres (docker-compose) with SQLite fallback for local dev

&#x20; - FastAPI for the API layer

&#x20; - Dashboard: React + Vite + Tailwind + Recharts (preferred) — Streamlit is

&#x20;   an acceptable faster-to-build fallback, see Section 7

&#x20; - pytest for all tests

&#x20; - GitHub Actions for CI and the scheduled scraping cron



DELIVERABLES FOR EVERY MODULE

&#x20; - Working code in its folder

&#x20; - Unit tests in a `tests/` subfolder, runnable via `pytest`

&#x20; - A README.md in that folder explaining what it does and how to run it alone

&#x20; - Type hints throughout, docstrings on all public functions



Now create the full folder skeleton above with placeholder files, a root

README.md with setup instructions, docker-compose.yml wiring Postgres + API +

dashboard together, and .env.example. Do not implement business logic yet —

that happens in the per-module prompts that follow. Just get the skeleton,

the frozen interfaces (as actual Python dataclasses/Pydantic models/SQL DDL),

and the DEMO\_MODE plumbing in place so 6 people can build in parallel.

