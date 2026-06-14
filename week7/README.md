# Week 7 — Cost Optimization & Continuous Learning

## Overview

This final week you'll optimize your agent's cost and implement a feedback loop for continuous improvement:
- **Cost Analysis** — Breakdown costs by component and identify expensive queries
- **Optimization Strategies** — Caching, model selection, retrieval optimization
- **Feedback Loop** — Collect user corrections and measure improvement

**Key concept:** Agents are never perfect. Collect feedback, measure what breaks, and continuously improve.

---

## Setup

### 1. Install Dependencies

```bash
cd week7
pip install -r requirements.txt
```

### 2. Copy Files from Week 6

Copy your completed files from the previous weeks into the week7/ folder before starting:

```bash
cp ../week6/app_starter.py .
cp ../week6/access_control_starter.py .
```

**Important:** All your work this week should live inside the `week7/` folder. Do not modify your Week 5 or Week 6 files — treat `week7/` as a self-contained project. Once copied, you will only edit files inside `week7/`.

Your copied files should already have the `Agent` class, all three tools, and the three guardrail classes (`AccessController`, `RateLimiter`, `CostEnforcer`) implemented. Week 7 adds cost optimization and a feedback loop on top of that foundation.

---

## Your Tasks

### 1. Implement CostAnalyzer
In `cost_optimization_starter.py`, implement `CostAnalyzer`:

```python
class CostAnalyzer:
    """Analyze and track query costs."""

```

### 2. Implement OptimizationStrategy

In the same file, implement `OptimizationStrategy`:

```python
class OptimizationStrategy:
    """Optimize agent costs through caching, model selection, etc."""

```

### 3. Implement FeedbackLoop

In the same file, implement `FeedbackLoop`:

```python
class FeedbackLoop:
    """Collect and validate user corrections."""

```

Here is an example of what a correction entry can look like, although you are free to store corrections in any format you deem fit:

```json
{
  "original_query": "What is the travel policy for flights over 8 hours?",
  "user_role": "engineer",
  "original_answer": "There is no specific policy for 8+ hour flights.",
  "corrected_answer": "Employees can book business class for flights over 8 hours with manager approval."
}
```

### 4. Write Tests, Run and Verify Your Implementation

A test structure is provided at the bottom of `cost_optimization_starter.py`. Once you've implemented the three classes, add your own test cases and run:

Run:
```bash
cd week7
python3 cost_optimization_starter.py
```

Feel free to modify or extend the test block to cover edge cases for all three classes.

---

## Deliverables

1. **`cost_optimization_starter.py`** — CostAnalyzer, OptimizationStrategy, FeedbackLoop + implementation code which runs tests
2. **One report with screenshots and documentation if necessary** — screenshots showing output of the tests written in the `__main__` code chunk of the `cost_optimization_starter.py` file + description of code structure if it was modified significantly


## Grading

| Criterion | Weight |
|-----------|--------|
| Cost analysis (breakdown by component working) | 20% |
| Spike detection (identifies expensive queries) | 20% |
| Optimization strategies (caching, model selection) | 20% |
| Feedback loop (collects corrections, measures impact) | 20% |
| Report with screenshots showing agent output and tests passing | 20% |

---

## Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues.

---

## Course Complete! 

You've built a complete agent system:
- **Week 5** - Agent with tools and LLM
- **Week 6** - Access control and guardrails  
- **Week 7** - Cost optimization and feedback loops

Congratulations on completing the Operationalizing AI course!
