# AirFareX Airfare Price Index Methodology Specification ($\text{APIX\_v1}$)

## 1. Mathematical Formulation

The AirFareX platform constructs a high-frequency Consumer Price Index (CPI) transport augmentation indicator for domestic air travel in India.

### 1.1 Representative Fare Selection
Airfare price distributions exhibit right-skewness due to premium last-minute pricing. Therefore, the representative fare $P_{i,t,l}$ for route $i$, observation date $t$, and lead-time bucket $l \in \{1, 7, 15, 30, 45\}$ is calculated as the **median total fare**:

\[
P_{i,t,l} = \text{Median} \left( \{ \text{total\_fare}_k \mid k \in \text{Route } i, \text{ Date } t, \text{ LeadTime } l, \text{ Outlier } = \text{False} \} \right)
\]

### 1.2 Route Price Index
For route $i$ on date $t$:
\[
I_{i,t} = \left( \frac{P_{i,t}}{P_{i,0}} \right) \times 100
\]
where $P_{i,0}$ is the baseline median price during the 30-day base period.

### 1.3 National Airfare Price Index ($\text{APIx}$)
The national index is calculated as the weighted aggregate across all $N$ active corridors:
\[
\text{APIx}_t = \frac{\sum_{i=1}^{N} w_i \cdot I_{i,t}}{\sum_{i=1}^{N} w_i}
\]
where $\sum w_i = 1.0$.

---

## 2. Advance Purchase Window Bucketing

To measure lead-time price elasticities, prices are tracked across 5 distinct advance purchase lead-time buckets:
- $T+1$: 1 day advance booking (immediate demand surge)
- $T+7$: 1 week advance booking
- $T+15$: 2 weeks advance booking
- $T+30$: 1 month advance booking
- $T+45$: 1.5 months advance booking (early bird baseline)

---

## 3. Demo Weights Notice

Weights specified in `config/routes.yaml` are explicitly labeled as `DEMO_WEIGHTS`. They are fully configurable to be replaced with official DGCA/MoSPI passenger flow weights without code changes.
