# AirFareX 5–7 Minute Evaluation & Presentation Script

## Demo Agenda & Flow

### 1. Introduction & Problem Statement (1 Minute)
- **Presenter**: "Official CPI transport indicators in India rely on manual or static surveys. AirFareX introduces a real-time, statistically defensible Airfare Price Index ($\text{APIX\_v1}$) tracking top domestic flight corridors like DEL-BOM, DEL-BLR, and BOM-BLR."
- **Key Highlight**: Point to the **DEMO MODE** notice and explain ethical compliance (no CAPTCHA bypass, strict robots.txt adherence).

### 2. High-Frequency Index Dashboard (2 Minutes)
- **Action**: Show main dashboard KPI Cards (APIx Index = 102.26, +2.26% 30-Day Change, 11,460 Quotes).
- **Action**: Interact with the **India Airfare Price Index (APIx)** line chart. Switch timeframe from 30D to 7D, and filter by route (e.g. `DEL-BOM`).
- **Action**: Show **Advance Purchase Route Fare Matrix** heatmap and **Lead-Time Price Elasticity Curve** ($T+1$ to $T+45$).

### 3. Carrier Comparison & Component Fee Breakdown (1 Minute)
- **Action**: Point out **Carrier Median Fare Comparison** (IndiGo vs Air India vs Vistara vs Akasa).
- **Action**: Show **Fare Component Breakdown** stacked bar chart (Base Fare, Taxes, Airport Charges, Fuel Surcharges, Convenience Fees).

### 4. Data Quality & Data Explorer (1 Minute)
- **Action**: Click on **Data Quality Panel** (Valid quotes, MAD/IQR outliers flagged, duplicates flagged, 98.4% mean quality score).
- **Action**: Navigate to **Data Explorer (`/data`)**. Filter by route `DEL-BOM` and click **Export CSV**.

### 5. Index Methodology & Backtesting (1 Minute)
- **Action**: Click **"How is this calculated?"** to open the Methodology Drawer.
- **Presenter**: Explain Laspeyres formula $I_{i,t} = (P_{i,t} / P_{i,0}) \times 100$, median pricing resistance to skewness, and configurable `DEMO_WEIGHTS`.
- **Action**: Run `python scripts/run_backtest.py` in terminal to show MAE, RMSE, MAPE, and Directional Accuracy.
