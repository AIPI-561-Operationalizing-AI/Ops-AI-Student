# Week 6 — Access Control & Monitoring

## Overview

This week you'll add guardrails to the Week 5 agent:
- **Access Control** — Enforce role-based access to documents and sensitive fields
- **Rate Limiting** — Limit queries per minute per user
- **Cost Enforcement** — Prevent users from exceeding their budget
- **Monitoring** — Track health metrics and detect anomalies

This week builds directly on your Week 5 agent. You will implement three guardrail classes in `access_control_starter.py`, then integrate them into your Week 5 `app_starter.py`.

**Key concept:** Guardrails prevent misuse and unauthorized access. They should block requests *before* they reach the LLM, not after.

---

## Setup

### 1. Install Dependencies

```bash
cd week6
pip install -r requirements.txt
```

### 2. Copy Files from Week 5
Copy your completed Week 5 files into the `week6/` folder before starting. Below is the command to follow if you followed the code structure provided in the assignment. **If you made significant changes to the code structure or arranged your code across multiple files for Assignment 5, make sure to replicate that setup here and implement the rest of the tasks according to your logic.**

```bash
cp ../week5/app_starter.py .
```

**Important:** All your work this week should live inside the `week6/` folder. Do not modify your Week 5 files — treat `week6/` as a self-contained project that happens to start from your Week 5 code. Once copied, you will only edit files inside `week6/`.

Your copied app_starter.py should already have `Agent`, `EmployeeLookupTool`, `PolicySearchTool`, and `ExpenseQueryTool` implemented. Week 6 adds guardrails on top of that foundation.

### 3. Review the Access Control Policy

A `data/access_control.json` file is already provided. It defines five roles (`engineer`, `manager`, `hr`, `finance`, `executive`), their permissions, and which fields are considered sensitive. Open it and read through it before starting the tasks — your `AccessController` implementation will load and use this file directly.

**A note on roles:**

This week uses a simplified role system with five roles: `engineer`, `manager`, `hr`, `finance`, and `executive`. When testing, you will pass roles in manually as strings (e.g. `user_role="manager"`). Note that `data/techcorp.db` stores job levels as codes like `IC3` or `M1` — these do not map directly to the five roles above, so do not try to derive a user's role from the database this week. Similarly, `data/policies.json` uses a separate seniority vocabulary (`director`, `vp`, etc.) for expense limits — this is used by your Week 5 `ExpenseQueryTool` and is independent of the access control role system.

For example, when calling your agent, you can pass `user_role` explicitly. For example, `agent.query("What is Sarah's salary?", user_id="user1", user_role="engineer")` should return a redacted response, while `user_role="hr"` should return the full answer. The role is essentially a caller-supplied parameter, not something derived from data.

---

## Your Tasks

### 1. Implement AccessController

In `access_control_starter.py`, implement the `AccessController` class:

```python
class AccessController:
    """Enforce role-based access control."""

    def __init__(self, access_policy_path: str):
        # TODO: Load JSON policy
        # TODO: Store in memory
        pass

    def can_view_document(self, role: str, document: Dict) -> bool:
        """Check if role can view this document."""
        # TODO: Check document sensitivity vs role permissions
        pass

    def can_view_field(self, role: str, field_name: str) -> bool:
        """Check if role can view this field."""
        # TODO: Check field in sensitive_fields
        pass

    def redact_response(self, role: str, response: str) -> str:
        """Redact sensitive fields from response."""
        # TODO: Find sensitive fields in response
        # TODO: Replace with [REDACTED]
        pass

    def log_access(self, role: str, resource: str, allowed: bool, field: str = None):
        """Log access attempt for audit."""
        # TODO: Append to audit_log with timestamp
        pass

    def filter_documents(self, role: str, documents: List) -> List:
        """Filter documents based on role."""
        # TODO: Return only documents role can view
        pass
```

### 2. Implement RateLimiter

In the same file, implement `RateLimiter`:

```python
class RateLimiter:
    """Rate limit queries per user per minute."""

    def __init__(self, max_queries_per_minute: int = 30):
        pass

    def is_allowed(self, user_id: str) -> bool:
        """Check if user can make another query."""
        # TODO: Track query times per user
        # TODO: Count queries in last 60 seconds
        # TODO: Return False if at limit
        pass

    def get_remaining_queries(self, user_id: str) -> int:
        """Get remaining queries for user."""
        # TODO: Return max - current queries in last minute
        pass
```

### 3. Implement CostEnforcer

In the same file, implement `CostEnforcer`:

```python
class CostEnforcer:
    """Enforce budget limits per role."""

    def __init__(self, policy_path: str = None):
        # TODO: Load role budgets:
        # engineer: $100/month
        # manager: $500/month
        # hr: $200/month
        # finance: $500/month
        # executive: $1000/month
        pass

    def add_cost(self, user_id: str, role: str, cost: float):
        """Track spending for user."""
        # TODO: Add to user_spending dict
        pass

    def can_afford_query(self, user_id: str, estimated_cost: float) -> bool:
        """Check if user has budget remaining."""
        # TODO: Get user's budget
        # TODO: Get user's spending so far
        # TODO: Return True if estimated_cost <= remaining_budget
        pass

    def get_budget_remaining(self, user_id: str) -> float:
        """Get remaining budget for user."""
        # TODO: Calculate budget - spending
        pass
```

### 4. Integrate with Week 5 Agent

Update your Week 5 `app_starter.py` to use access control:

```python
class Agent:
    def __init__(self, db_path: str, api_key: str = None):
        # ... existing code ...
        self.access_controller = AccessController("data/access_control.json")
        self.rate_limiter = RateLimiter(max_queries_per_minute=30)
        self.cost_enforcer = CostEnforcer()

    def query(self, user_query: str, user_id: str, user_role: str = "engineer"):
        # Check access
        if not self.rate_limiter.is_allowed(user_id):
            return {"error": "Rate limit exceeded"}

        estimated_cost = 0.01  # Estimate
        if not self.cost_enforcer.can_afford_query(user_id, estimated_cost):
            return {"error": "Budget exceeded"}

        # ... execute query ...
        
        # Track cost
        actual_cost = 0.005  # Actual
        self.cost_enforcer.add_cost(user_id, user_role, actual_cost)
        
        # Redact response
        answer = result["answer"]  # answer from your Week 5 agent's query() method
        answer = self.access_controller.redact_response(user_role, answer)
        
        return {"answer": answer, "cost": actual_cost}
```

---

## Testing

### Run and Verify Your Implementation

A test block is provided at the bottom of `access_control_starter.py`. Once you've implemented the three classes, run it to verify everything works:

```bash
cd week6
python3 access_control_starter.py
```

You should see:

```markdown
Testing AccessController...
  can_view_field: PASSED
  filter_documents: PASSED

Testing RateLimiter...
  is_allowed: PASSED

Testing CostEnforcer...
  can_afford_query: PASSED

All tests passed!
```
Feel free to modify or extend the test implementation block.

---

## Deliverables

1. **`access_control_starter.py`** — the main code file with AccessController, RateLimiter, CostEnforcer classes
2. **Updated `app_starter.py` copied over from Week 5** — Integrated with access control guardrails
3. **One report with screenshots of output** — Test queries with different roles (allowed/denied/redacted)

## Grading

| Criterion | Weight |
|-----------|--------|
| AccessController (role-based access working) | 30% |
| RateLimiter (tracks queries per minute) | 20% |
| CostEnforcer (tracks budgets, blocks when exceeded) | 20% |
| Integration with agent from week 5 (agent uses all guardrails) | 20% |
| Report showing satisfactory output | 10% |

---

## Common Issues

**Access control not working?** → See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Next Week

Week 7 will add:
- Cost optimization (caching, model selection, etc.)
- Feedback loops (learning from corrections)
- Advanced monitoring

Implement solid access control this week!
