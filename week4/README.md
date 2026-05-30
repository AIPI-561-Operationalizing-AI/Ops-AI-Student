# Week 4 — Monitoring, Drift Detection & Retraining Strategy

## Before You Start

1. Read [READING.md](READING.md) - data drift vs concept drift, statistical tests, retraining strategies
2. Review [BASELINE_METRICS.md](BASELINE_METRICS.md) - reference values from healthy system (Jan 1-15, 2026)
3. Install dependencies: `pip install pandas pyarrow scipy scikit-learn numpy`

## Assignment

Your Week 2-3 API is running well. But new data (Feb 2-28) shows quality/performance degradation (you can filter `demand_enriched_week4.parquet` to this window to check new data). Add automated monitoring to detect drift and trigger retraining.

**Your tasks:**
1. Define metrics to catch drift (distributions, outliers, performance)
2. Set alert thresholds
3. Add monitoring workflow to GitHub Actions (runs on schedule)
4. **YOU DECIDE:** How often to monitor? (hourly? daily? weekly?)
5. When drift detected: alert ops and assess if retraining needed

**Deliverables:**
- `.github/workflows/monitor-drift.yml` - monitoring workflow
- `scripts/compute_metrics.py` - metric calculations
- `scripts/detect_drift.py` - drift detection logic
- Tests for monitoring
- **Report:**
  - Metrics defined + thresholds
  - Monitoring schedule choice + justification
  - Retraining trigger strategy

**Note:** A running GKE cluster is NOT expected in your final deliverables. Similar to previous assignments, you are not required to spend GCP credits on maintaining a cluster. If you choose to deploy a cluster, please include screenshots in your report clearly describing how it was operated in the context of this assignment.

---

## What You Have

```
week4/
├── .github/workflows/
│   └── monitor-drift.yml      (TEMPLATE: Fill in TODOs - decide frequency, implement monitoring)
├── data/
│   ├── demand_enriched_baseline.parquet  (Jan 1-15, healthy)
│   ├── demand_enriched_week3.parquet     (Jan 16-Feb 1, corrupted)
│   └── demand_enriched_week4.parquet     (full history 2023–Feb 2026; drift injected Feb 2–28, 2026)
├── BASELINE_METRICS.md        (reference values)
├── scripts/
│   ├── metric_template.py     (TEMPLATE: Implement metrics)
│   ├── detect_drift.py        (TEMPLATE: Implement drift detection)
│   ├── compute_metrics.py     (YOU WRITE: Call metrics, report results)
│   └── test_monitoring.py     (YOU WRITE: Tests for metrics/drift)
└── README.md (this file)
```

**All data files provided. All work happens in week4/.**

### GitHub Actions Workflow

You have a template `.github/workflows/monitor-drift.yml`. Fill in the TODOs:
1. Choose monitoring frequency (hourly? daily? weekly?)
2. Implement metric computation step
3. Implement drift detection step
4. Alert ops if thresholds breached (create GitHub issue)

### How the Scripts Fit Together

- `metric_template.py` — defines the `MetricComputer` class with 8 metric stubs. Implement the metric logic here.
- `compute_metrics.py` — **you write this**. Import `MetricComputer`, load baseline and new data, run all metrics, check thresholds, and write results to `metrics-*.json`. This is what CI runs.
- `detect_drift.py` — **you write the body of this**. Run statistical tests (KS, PSI) to identify drift patterns. This is also run by CI.

CI runs both `compute_metrics.py` and `detect_drift.py` independently.

---

## Setup: No LFS Involved

Make sure data files have been downloaded fully without any LFS pointers. Pull or re-clone the course repo if you face issues.
---

## Baseline Understanding

**Baseline period: Jan 1-15, 2026**
- Model trained on this data
- Accuracy: approximately 91% overall
- Null rates: <0.5%
- No duplicates
- No drift

See [BASELINE_METRICS.md](BASELINE_METRICS.md) for detailed reference values.

---

## Part 1: Add Monitoring Workflow

Edit the template `.github/workflows/monitor-drift.yml`:

**YOU DECIDE:** How often should this run?

**Options:**
- **Every hour:** Catch drift immediately (frequent alerts, higher cost)
- **Every 4 hours:** Good balance
- **Daily:** Cost-effective, easy to act on
- **Weekly:** For long-term trend detection
- **On-demand:** Manual trigger + scheduled backup

**Template TODOs in `.github/workflows/monitor-drift.yml`:**
1. Set cron schedule frequency (see options above)
2. Implement `compute_metrics.py` step (load data, run metrics, report)
3. Implement `detect_drift.py` step (run statistical tests, print findings)
4. Fill in the alert/issue creation logic
5. Test locally before committing

**Justification in report:** Why that frequency? What's the detection lag vs cost trade-off?

---

## Part 2: Design Monitoring Framework

Implement at least 5 of the 8 provided metric stubs in order to detect four types of problems:
1. **Data quality issues** (nulls, duplicates, outliers)
2. **Data drift** (input distribution changed)
3. **Concept drift** (model accuracy degraded)
4. **Infrastructure problems** (lateness, missing data)

### Metric Template

For each metric, specify:
- **Computation**: How to calculate it
- **Baseline value**: Expected healthy value
- **Alert threshold**: When to alert
- **Frequency**: How often to compute
- **Segmentation**: Global? Per-zone? Per-hour?

### Example: Metric #1 (Accuracy by Zone)

```
Metric: Accuracy by Zone
- Computation: For each zone, % predictions == actual_pickups
- Baseline: 85-95% per zone (from BASELINE_METRICS.md)
- Alert threshold: <80% for any zone
- Frequency: Daily at 9am (after 24h ground truth lag)
- Segmentation: Per zone (57 zones) + global rollup
- Action: If alert fires, check if recent data shows distribution shift
```

### Starter Code

`week4/scripts/metric_template.py` has 8 metric stubs. Implement at least 5 of them based on your design.

**Your metrics should cover:**
- Performance (accuracy overall, by segment)
- Data quality (nulls, duplicates, outliers)
- Data drift (distribution shifts - KS test, PSI)
- Model health (prediction distribution, staleness)

For each metric, decide:
- How to compute it
- Baseline value (from BASELINE_METRICS.md)
- Alert threshold
- Check frequency
- Segmentation (global? per-zone? per-hour?)

---

## Part 3: Detect Drift

Analyze Feb 2-28 data compared to Jan 1-15 baseline. Find 4+ distinct drift patterns.

### What to Detect

Write code in `week4/scripts/detect_drift.py` to find 4+ distinct drift patterns.

Compare Feb 2-28 data to Jan 1-15 baseline using statistical tests:

**Data Drift (Distribution Shift):**
- Use KS test, PSI, chi-square
- Example: trip_count distribution changed significantly

**Concept Drift (Performance Shift):**
- Compare accuracy/performance by segment
- Example: Zone 42 accuracy dropped from 92% to 75%

**Segment-level Issues:**
- Not just global metrics—check by zone, hour, day-of-week
- Find which segments degraded

For each pattern you find, document:
- What drifted (which feature/segment)
- Type (data drift, concept drift, both)
- Statistical evidence (test name, p-value, magnitude)
- Impact (how much worse for predictions)

---

## Part 4: Design Retraining Strategy

### Define Retraining Triggers

When should you retrain? Examples:
- If zone accuracy drops below X%
- If PSI > threshold
- If KS test p-value < threshold
- On schedule (weekly, bi-weekly, etc.)

You decide the thresholds based on your business needs.

### Retraining Pipeline

Describe the workflow: detect → train → validate → deploy → fallback

Key decisions:
- What data to retrain on? (last 7 days? 30 days? all data?)
- How to validate new model? (offline testing, shadow mode, canary?)
- How to rollback if it fails? (keep previous version, automatic triggers?)

### Model Versioning

How do you store and track models?
- Where? (cloud storage, local, registry?)
- What metadata? (training date, accuracy, data used?)
- How long keep old versions? (for rollback safety?)

Be operational: think about what you'd actually do in production.

---

## Part 5: Write Code (Optional)

If implementing monitoring code:

- `compute_metrics.py`: Load baseline and new data, run metrics, report results and alerts
- `detect_drift.py`: Run statistical tests, print findings
- `test_monitoring.py`: Tests that verify your metrics/drift detection work correctly

No specific format required. Show your work, document your findings.

---

## Deliverables Summary

1. **Drift Detection Report**
   - Around 4 drift patterns with quantitative evidence
   - Tables/plots showing the drift
   - Hypotheses on root causes

2. **Monitoring Framework**
   - At least 5 of 8 metrics specified (computation, baseline, threshold, frequency, segmentation)
   - Dashboard mockup or metric list
   - Alert thresholds and interpretation

3. **Retraining Strategy**
   - Trigger conditions (performance drop %, drift p-value, schedule)
   - Retraining pipeline (steps, timeline)
   - Validation approach (offline testing, shadow, canary)
   - Model versioning and rollback procedure
   - Frequency (weekly, bi-weekly, on-demand)

4. **Architecture Diagram**
   - Baseline data → monitoring job → metrics → drift detection → retraining trigger → training → validation → deployment/rollback

5. **Code** (Optional)
   - `compute_metrics.py` (metrics implementation)
   - `detect_drift.py` (drift detection)
   - `test_monitoring.py` (tests)

---

## Grading

| Criterion | Weight |
|-----------|--------|
| Drift detection (identifies patterns with evidence) | 30% |
| Monitoring design (metrics, thresholds, segmentation) | 25% |
| Retraining strategy (triggers, pipeline, validation) | 20% |
| Code implementation (scripts work, produce output) | 15% |
| Report | 10% |

---

## Key Principles

**Segment everything:** Global metrics hide failures. Always segment by zone, hour, day-of-week where applicable.

**Combine reactive + proactive:**
- Reactive: Accuracy monitoring (24-48h lag) catches problems after they happen
- Proactive: Drift detection (real-time) catches problems before accuracy drops

**Cost of retraining:** Compute + storage + labor. Retrain when signal is clear, not for every fluctuation.

**Validate before deploying:** Never deploy a model not tested first. Shadow mode or canary is gold standard.

---

## Common Mistakes

**Metrics too coarse:** "Accuracy is 90%" masks 65% in specific zone. Segment.

**Drift without action:** "PSI=0.23" is data. "PSI=0.23 → retrain → accuracy improves to 91%" is insight.

**Retraining without validation:** "Retrain weekly" can deploy worse models. "Retrain weekly, validate, deploy only if >= current" is safe.

**Silent degradation:** New model deployed but nobody knows it's performing worse. Use shadowing + automatic rollback.

---

## Due

End of Week 4 (see syllabus)
