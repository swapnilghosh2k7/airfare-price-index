# Econometric & Statistical Methodology for APIx
## Real-time Airfare Price Index for CPI Augmentation

### 1. Executive Summary
The National Statistical Office (NSO), Ministry of Statistics and Programme Implementation (MoSPI), computes the headline Consumer Price Index (CPI) to track retail inflation in India. The Reserve Bank of India (RBI) utilizes this index as the nominal anchor for the Flexible Inflation Targeting (FIT) monetary framework.

Currently, airfare prices within the **Transport and Communication** subgroup are surveyed manually from a restricted selection of physical ticketing counters and travel agents on a monthly schedule. Given that >90% of domestic bookings are now transacted through algorithmic Online Travel Aggregators (OTAs) and airline dynamic yield engines, traditional collection methods suffer from significant sampling latency and miss intraday, day-of-week, and advance-purchase volatility.

**APIx (Airfare Price Index)** addresses this gap by implementing an automated, high-frequency, statistically rigorous price index.

---

### 2. Representative Route Basket & DGCA Weighting
The platform monitors 20 high-density domestic city-pairs accounting for >85% of total domestic revenue passenger kilometers (RPKs):

| Route Code | Corridor | Origin | Destination | Base Traffic Weight $W_r$ |
|---|---|---|---|---|
| **DEL-BOM** | North-West | Delhi (DEL) | Mumbai (BOM) | 0.125 (12.5%) |
| **BOM-DEL** | West-North | Mumbai (BOM) | Delhi (DEL) | 0.120 (12.0%) |
| **DEL-BLR** | North-South | Delhi (DEL) | Bengaluru (BLR) | 0.085 (8.5%) |
| **BLR-DEL** | South-North | Bengaluru (BLR) | Delhi (DEL) | 0.080 (8.0%) |
| **BOM-BLR** | West-South | Mumbai (BOM) | Bengaluru (BLR) | 0.065 (6.5%) |
| **BLR-BOM** | South-West | Bengaluru (BLR) | Mumbai (BOM) | 0.060 (6.0%) |
| **DEL-HYD** | North-South | Delhi (DEL) | Hyderabad (HYD) | 0.055 (5.5%) |
| **HYD-DEL** | South-North | Hyderabad (HYD) | Delhi (DEL) | 0.050 (5.0%) |
| **DEL-CCU** | North-East | Delhi (DEL) | Kolkata (CCU) | 0.050 (5.0%) |
| **CCU-DEL** | East-North | Kolkata (CCU) | Delhi (DEL) | 0.045 (4.5%) |
| **MAA-DEL** | South-North | Chennai (MAA) | Delhi (DEL) | 0.040 (4.0%) |
| **DEL-MAA** | North-South | Delhi (DEL) | Chennai (MAA) | 0.040 (4.0%) |
| **BOM-HYD** | West-South | Mumbai (BOM) | Hyderabad (HYD) | 0.035 (3.5%) |
| **HYD-BOM** | South-West | Hyderabad (HYD) | Mumbai (BOM) | 0.030 (3.0%) |
| **BOM-MAA** | West-South | Mumbai (BOM) | Chennai (MAA) | 0.030 (3.0%) |
| **MAA-BOM** | South-West | Chennai (MAA) | Mumbai (BOM) | 0.025 (2.5%) |
| **BLR-HYD** | South-South | Bengaluru (BLR) | Hyderabad (HYD) | 0.030 (3.0%) |
| **DEL-PNQ** | North-West | Delhi (DEL) | Pune (PNQ) | 0.030 (3.0%) |
| **BOM-GOI** | West-West | Mumbai (BOM) | Goa (GOI) | 0.025 (2.5%) |
| **DEL-GOI** | North-West | Delhi (DEL) | Goa (GOI) | 0.020 (2.0%) |

**Constraint:**
$$\sum_{r=1}^{20} W_r = 1.000$$

---

### 3. Advance Purchase Horizon Stratification
Dynamic airline pricing algorithms shift fares systematically depending on booking lead-time. The system samples five explicit horizons:
- **T+1 (1 day lead):** Last-minute distress/business traveler surge.
- **T+7 (7 days lead):** Near-term planning escalation window.
- **T+15 (15 days lead):** Neutral reference equilibrium window.
- **T+30 (30 days lead):** Advance domestic leisure booking window.
- **T+45 (45 days lead):** Early-bird promotional tier with maximum inventory availability.

---

### 4. Mathematical Formulation of APIx
APIx uses a transparent Laspeyres-type weighted price relative index:

#### 4.1 Route-Level Weighted Average
For route $r$ on date $t$:
$$\bar{P}_{r, t} = \frac{1}{N_{r, t}} \sum_{i=1}^{N_{r, t}} P_{r, t, i}$$
where $P_{r, t, i}$ is the clean total economy fare of observation $i$.

#### 4.2 Price Relative Calculation
Relative to a fixed base reference period $t_0$:
$$PR_{r, t} = \left( \frac{\bar{P}_{r, t}}{\bar{P}_{r, t_0}} \right) \times 100$$

#### 4.3 Composite APIx Index
The headline daily index is computed as:
$$APIx_t = \sum_{r \in \text{Routes}} W_r \times PR_{r, t}$$

---

### 5. Data Cleaning and Outlier Detection Pipeline
Observations pass through a 12-step validation gate before entering index aggregation:
1. **Schema Check:** Required non-null fields (route, airline, source, fare, dates).
2. **Missing-Value Imputation / Rejection.**
3. **Unique Quote Deduplication:** Signature `(route, airline, travel_date, flight_no, total_fare)`.
4. **Currency Standardization:** Rejection of non-INR quotes.
5. **Component Equality:** $|\text{Base} + \text{Fuel} + \text{UDF} + \text{Airport} + \text{Taxes} + \text{Fees} - \text{Total}| \le 2.0$.
6. **Price Bounds:** Fares $< ₹500$ or $> ₹150,000$ discarded.
7. **Stratified Outlier Detection:** Per `(route, advance_window)` stratum:
   - **IQR:** $IQR = Q_3 - Q_1$, bounds $[Q_1 - 1.5 \times IQR, Q_3 + 1.5 \times IQR]$.
   - **Median Absolute Deviation (MAD):** $M_i = 0.6745 \times \frac{|x_i - \tilde{x}|}{MAD}$. Observations with $|M_i| > 3.0$ logged as outliers.
8. **Sold-Out Flight Handling.**
9. **Fleet & Route Registry Validation.**
10. **Chronological Validity:** $\text{Search Date} \le \text{Travel Date}$.
11. **Advance Window Standardization.**
12. **Audit Logging:** All discarded quotes persisted in `rejected_observations` with explicit rationale.

---

### 6. Backtesting & Model Validation
The APIx series is continuously backtested against regulatory DGCA tariff filings across five statistical dimensions:
- **Mean Absolute Error (MAE):** $\frac{1}{N} \sum |APIx_t - Ref_t|$
- **Mean Absolute Percentage Error (MAPE):** $\frac{1}{N} \sum \left| \frac{APIx_t - Ref_t}{Ref_t} \right| \times 100\%$
- **Root Mean Square Error (RMSE):** $\sqrt{\frac{1}{N} \sum (APIx_t - Ref_t)^2}$
- **Pearson Correlation ($r$):**
  $$r = \frac{\sum (APIx_t - \overline{APIx})(Ref_t - \overline{Ref})}{\sqrt{\sum (APIx_t - \overline{APIx})^2 \sum (Ref_t - \overline{Ref})^2}}$$
- **Mean Directional Bias:** $\frac{1}{N} \sum (APIx_t - Ref_t)$
