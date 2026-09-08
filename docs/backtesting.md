# AirFareX 30-Day Backtesting & Validation Specification

## 1. Overview

Backtesting is a critical requirement for evaluating the statistical accuracy, stability, and predictive tracking of the **AirFareX Airfare Price Index ($\text{APIX\_v1}$)**.

The backtesting framework compares daily calculated national aggregate APIx index values against a benchmark reference dataset over a 30-day historical window.

---

## 2. Evaluation Metrics

### 2.1 Mean Absolute Error (MAE)
Measures average absolute magnitude of index errors:
\[
\text{MAE} = \frac{1}{n} \sum_{t=1}^{n} \left| \text{APIx}_t - \text{Ref}_t \right|
\]

### 2.2 Root Mean Squared Error (RMSE)
Penalizes larger index deviations:
\[
\text{RMSE} = \sqrt{ \frac{1}{n} \sum_{t=1}^{n} (\text{APIx}_t - \text{Ref}_t)^2 }
\]

### 2.3 Mean Absolute Percentage Error (MAPE)
Measures relative percentage error:
\[
\text{MAPE} = \frac{100\%}{n} \sum_{t=1}^{n} \left| \frac{\text{APIx}_t - \text{Ref}_t}{\text{Ref}_t} \right|
\]

### 2.4 Pearson Correlation Coefficient ($r$)
Measures linear tracking alignment between APIx and reference values.

### 2.5 Directional Accuracy (%)
Percentage of days where day-over-day price index movement direction ($\text{sign}(\Delta \text{APIx})$) matches the reference benchmark direction ($\text{sign}(\Delta \text{Ref})$).

---

## 3. How to Run 30-Day Backtest

Run the command-line evaluation script:

```bash
python scripts/run_backtest.py
```

Sample Report Output:
```text
=================================================================
    AIRFAREX 30-DAY BACKTESTING EVALUATION REPORT (APIX_v1)
=================================================================
  Total Evaluation Period      : 30 Days (2026-08-05 to 2026-09-03)
  Calculated APIx Start / End  : 94.53 / 100.00
  Reference Benchmark Start/End: 100.00 / 105.70
-----------------------------------------------------------------
  Mean Absolute Error (MAE)    : 5.5129
  Root Mean Squared Error (RMSE): 6.5331
  Mean Absolute Percentage (MAPE): 5.33%
  Pearson Correlation Coefficient: 0.9412
  Directional Accuracy         : 86.21%
=================================================================
```

---

## 4. Reference Dataset Interface Notice

> [!NOTE]
> If official DGCA historical passenger fare statistics are provided by competent authorities, place the reference CSV in `data/reference/official_dgca_baseline.csv` to automatically evaluate APIx against official government statistics.
