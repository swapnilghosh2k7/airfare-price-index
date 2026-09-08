# AirFareX Project Roadmap & Milestone Tracker

## Overview

AirFareX is built incrementally across 12 structured milestones to guarantee complete stability, zero-error execution, and high test coverage.

---

## Milestone Breakdown & Status

| Milestone | Phase Description | Target Deliverables | Status |
|---|---|---|---|
| **M1** | Project Initialization & Architecture | Config files (`routes.yaml`, `sources.yaml`, `settings.yaml`), `architecture.md`, `project-roadmap.md`, `README.md`, `.env.example` | **COMPLETED** |
| **M2** | Database Schema & Models | SQLAlchemy models (`Route`, `Carrier`, `FareQuote`, `DataQualityRecord`, `IndexObservation`, `DataCollectionRun`), Session manager | **COMPLETED** |
| **M3** | Synthetic Airfare Engine | 30-day realistic airfare data generator script (`generate_demo_data.py`), advance purchase curves, seed-based reproducibility | **COMPLETED** |
| **M4** | Normalization & Data Quality | Deduplication hashing, MAD & IQR outlier detection, data quality scoring pipeline | **COMPLETED** |
| **M5** | Index Construction Engine | Laspeyres price index calculation ($\text{APIX\_v1}$), baseline median computation, weight aggregation | **COMPLETED** |
| **M6** | FastAPI REST API Backend | Full OpenAPI backend with `/api/fares`, `/api/index`, `/api/analytics`, `/api/data-quality`, `/api/routes` | **COMPLETED** |
| **M7** | React Vite Dashboard | Dark-themed analytics UI, KPI cards, APIx line charts, advance purchase heatmap, lead-time curves, Data Explorer | **COMPLETED** |
| **M8** | Analytics & Indicators | Volatility std-dev/CV, route inflation rates (1D/7D/30D), price elasticity, carrier dispersion | **COMPLETED** |
| **M9** | 30-Day Backtesting System | Historical backtesting framework comparing APIx index to baseline reference, reporting MAE, RMSE, MAPE | **COMPLETED** |
| **M10** | Provider Architecture | Abstract `FareProvider` interface, `MockFareProvider`, `DatasetFareProvider`, ethical scraper adapters | **COMPLETED** |
| **M11** | Dockerization & Deployment | `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, local startup shell scripts | **COMPLETED** |
| **M12** | Testing & Polish | Comprehensive unit & integration tests (85% backend coverage), math verification, demo documentation | **COMPLETED** |

---

## Deliverables Verification Matrix

- [x] Initial config files created in `config/`
- [x] Technical architecture documented in `docs/architecture.md`
- [x] Roadmap updated in `docs/project-roadmap.md`
- [x] Environment template `.env.example` generated
- [x] Database initialized with SQLAlchemy ORM models
- [x] 30 days demo data generated in `data/sample/fare_quotes.csv` (11,460 quotes)
- [x] Database populated with cleaned quotes and index calculations
- [x] Backend server tested and answering requests on `http://localhost:8000/api/health`
- [x] Frontend React Vite dashboard built with Recharts, Tailwind CSS & Lucide icons
- [x] Automated pytest suite green (18/18 passed) with 85% code coverage
