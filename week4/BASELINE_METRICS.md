# Week 4: Baseline Metrics Reference

## Overview

These are the **healthy system metrics** computed from the baseline period (Jan 1-15, 2026).

Use these values as your reference when detecting drift in Feb 2-28 data.

---

## Data Distribution Metrics

Please note that the actual metrics might vary slightly, and the values below are indicative. Please rely on what you actually find from the data files for your analysis.

### Trip Count (Target Variable)

| Statistic | Value |
|-----------|-------|
| **Mean** | ~14.1 trips / zone / 15min |
| **Std Dev** | ~19.2 |
| **Min** | 0 |
| **Max** | 213 |
| **P50 (Median)** | 6 |
| **P95** | 53 |
| **P99** | 91 |

### Feature Distributions (Jan 1-15 Baseline)

Null rates are 0.0 for all features.

---

## Data Quality Metrics

| Check | Baseline Value | Alert Threshold |
|-------|----------------|-----------------|
| **Null Rate (trip_count)** | 0.0% | >1% |
| **Null Rate (PULocationID)** | 0.0% | >1% |
| **Null Rate (lag features)** | 0.0% | >2% |
| **Duplicate Rows** | 0 | >0.5% of rows |

---

## Drift Detection Baselines

### KS Test (Kolmogorov-Smirnov)

When comparing Feb 2-28 data to Jan 1-15 baseline:

| Feature | Alert Threshold (p-value) |
|---------|---------------------------|
| **trip_count** | <0.05 |
| **hour** | <0.05 |
| **dayofweek** | <0.05 |

**Interpretation:** If p-value < 0.05, the distributions are significantly different.

### Population Stability Index (PSI)

| Feature | Alert Threshold |
|---------|-----------------|
| **trip_count** | >0.25 |
| **hour** | >0.25 |
| **dayofweek** | >0.25 |

**Interpretation:**
- PSI = 0: Identical distributions
- PSI < 0.10: Negligible change
- 0.10 < PSI < 0.25: Small change (monitor)
- PSI > 0.25: Significant change (investigate/retrain)

---

## Alert Thresholds

| Metric | Healthy | Warning | Critical | Action |
|--------|---------|---------|----------|--------|
| **Null Rate** | <0.5% | 0.5-1% | >1% | Check data pipeline |
| **KS p-value (drift)** | >0.05 | 0.01-0.05 | <0.01 | Significant drift detected |
| **PSI** | <0.10 | 0.10-0.25 | >0.25 | Recommend retrain |
| **Duplicates** | 0% | <0.5% | >0.5% | Data quality issue |

---

## Example: How to Use These Metrics

```python
# Load baseline and new data
baseline = pd.read_parquet("week4/data/demand_enriched_baseline.parquet")
new_data = pd.read_parquet("week4/data/demand_enriched_week4.parquet")

# Compute mean trip count
baseline_mean = baseline['trip_count'].mean()  # Should be ~14.1
new_mean = new_data['trip_count'].mean()

# Check if shift is significant
shift_pct = (new_mean - baseline_mean) / baseline_mean * 100

if abs(shift_pct) > 10:
    print(f"Trip count shifted {shift_pct:.1f}% — investigate")
```

---

## Notes

- These baselines are computed from Jan 1-15, 2026 data
- Baseline dataset has zero duplicates and minimal null values
- Feb 2-28 data shows drift patterns; use KS test and PSI to quantify them
- Student task: implement metrics in Week 4 and identify drifts using these thresholds

---
