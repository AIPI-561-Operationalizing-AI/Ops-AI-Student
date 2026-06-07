"""
Week 6: Access Control, Rate Limiting & Cost Enforcement Starter Template

Implement three guardrails:
1. AccessController - role-based document/field access control
2. RateLimiter - limit queries per minute per user
3. CostEnforcer - enforce budget limits per role
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
from time import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# TASK 1: Implement AccessController
# ============================================================================


class AccessController:
    """Enforce role-based access control."""

    def __init__(self, access_policy_path: str):
        """Load access control policy.

        TODO:
        1. Load JSON policy from access_policy_path
        2. Store in self.policy
        3. Initialize audit_log list for tracking access attempts
        """
        # TODO: implement
        self.policy = {}
        self.audit_log = []

    def can_view_document(self, role: str, document: Dict[str, Any]) -> bool:
        """Check if role can view document based on sensitivity level.

        TODO: Implement document visibility rules
        - Check document's sensitivity level (Public/Internal/Confidential/Restricted)
        - Check if role has permission for that sensitivity
        - Look up self.policy["document_access"][sensitivity] to get the list of roles allowed
        - Example:
          * public → all roles can view
          * internal → engineer, manager, hr, finance, executive
          * confidential → manager, hr, finance, executive
          * restricted → hr, executive only
        """
        # TODO: implement
        return False

    def can_view_field(self, role: str, field_name: str) -> bool:
        """Check if role can view a sensitive field.

        TODO: Check self.policy["sensitive_fields"]
        - Look up field in policy
        - Check if role is in visibility list
        - Example: salary field visible to ["manager", "hr"] only
        """
        # TODO: implement
        return False

    def redact_response(self, role: str, response: str) -> str:
        """Redact sensitive fields from response.

        TODO: Find and replace sensitive fields
        1. Identify which fields role cannot view
        2. Use regex to find those fields in response
        3. Replace values with "[REDACTED]"
        4. Return modified response
        """
        # TODO: implement
        return response

    def log_access(self, role: str, resource: str, allowed: bool, field: str = None):
        """Log access attempt for audit trail.

        TODO: Append to audit_log dict with:
        - timestamp (use datetime.utcnow().isoformat())
        - role
        - resource
        - field (if applicable)
        - allowed (True/False)
        """
        # TODO: implement
        pass

    def filter_documents(
        self, role: str, documents: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Filter documents based on role permissions.

        TODO: Loop through documents
        1. For each document, call can_view_document(role, doc)
        2. Log the access attempt
        3. Keep only documents role can view
        """
        # TODO: implement
        return documents

    def get_audit_log(self) -> List[Dict[str, Any]]:
        """Return audit log entries."""
        return self.audit_log


# ============================================================================
# TASK 2: Implement RateLimiter
# ============================================================================


class RateLimiter:
    """Rate limit queries per user per minute."""

    def __init__(self, max_queries_per_minute: int = 30):
        """Initialize rate limiter.

        TODO: Store max limit and initialize per-user query tracking
        """
        self.max_queries_per_minute = max_queries_per_minute
        self.user_query_times = {}  # {user_id: [timestamps...]}

    def is_allowed(self, user_id: str) -> bool:
        """Check if user can make another query.

        TODO: Implement rate limiting
        1. Get current time
        2. For user_id, get all query times from last 60 seconds
        3. Count queries in that window
        4. If count < max_queries_per_minute, allow and record timestamp
        5. Otherwise, deny

        Return: True if allowed, False if rate limit exceeded
        """
        # TODO: implement
        return True

    def get_remaining_queries(self, user_id: str) -> int:
        """Get remaining queries for user in current minute.

        TODO: Calculate remaining queries
        1. Get queries in last 60 seconds
        2. Return (max - count) or 0 if negative
        """
        # TODO: implement
        return self.max_queries_per_minute


# ============================================================================
# TASK 3: Implement CostEnforcer
# ============================================================================


class CostEnforcer:
    """Enforce cost limits per user/role."""

    def __init__(self, policy_path: str = None):
        """Initialize cost enforcement.

        TODO: Set up role budgets (monthly limits)
        - engineer: $100
        - manager: $500
        - hr: $200
        - finance: $500
        - executive: $1000

        Also initialize user_spending dict to track per-user spending
        """
        # TODO: implement
        self.role_budgets = {}
        self.user_spending = {}  # {user_id: {"role": "engineer", "total": 50.0}}

    def add_cost(self, user_id: str, role: str, cost: float):
        """Record cost for user.

        TODO: Update user_spending
        1. If user_id not in dict, create entry with role and total=0
        2. Add cost to user's total
        """
        # TODO: implement
        pass

    def can_afford_query(self, user_id: str, estimated_cost: float) -> bool:
        """Check if user has budget remaining.

        TODO: Check budget
        1. Get user's role and budget
        2. Get user's spending so far
        3. Calculate remaining: budget - spending
        4. Return True if estimated_cost <= remaining

        Note: if user_id is not yet in user_spending, you have no role to look up their budget.
        One approach: add role as a parameter here, similar to add_cost().
        """
        # TODO: implement
        return True

    def get_budget_remaining(self, user_id: str) -> float:
        """Get remaining budget for user.

        TODO: Calculate and return
        - budget - (user's total spending)
        - Return 0 if negative
        """
        # TODO: implement
        return 0.0


# ============================================================================
# TASK 4: Integrate with Week 5 Agent
# ============================================================================

# Once you have implemented the three classes above, open your copied
# app_starter.py and update the Agent class to use them:
#
# 1. In Agent.__init__, add:
#       self.access_controller = AccessController("data/access_control.json")
#       self.rate_limiter = RateLimiter(max_queries_per_minute=30)
#       self.cost_enforcer = CostEnforcer()
#
# 2. Update Agent.query() to accept user_id and user_role parameters:
#       def query(self, user_query: str, user_id: str, user_role: str = "engineer")
#
# 3. At the start of query(), add guardrail checks:
#       if not self.rate_limiter.is_allowed(user_id):
#           return {"error": "Rate limit exceeded"}
#       if not self.cost_enforcer.can_afford_query(user_id, estimated_cost=0.01):
#           return {"error": "Budget exceeded"}
#
# 4. After getting the LLM answer, redact sensitive fields:
#       answer = self.access_controller.redact_response(user_role, answer)
#
# 5. After each query, track actual cost:
#       self.cost_enforcer.add_cost(user_id, user_role, actual_cost)


# ============================================================================
# TASK 5: Test Your Implementation
# ============================================================================

# A basic test suite is provided below to help you verify your implementation.
# Run it with: python3 access_control_starter.py
# You are free to modify or extend these tests as you see fit.

if __name__ == "__main__":
    """Quick test of access control functionality."""

    # Test AccessController
    print("Testing AccessController...")
    controller = AccessController("data/access_control.json")

    assert not controller.can_view_field(
        "engineer", "salary"
    ), "Engineer should not see salary"
    assert controller.can_view_field("hr", "salary"), "HR should see salary"
    assert controller.can_view_field("manager", "salary"), "Manager should see salary"
    assert not controller.can_view_field(
        "engineer", "ssn"
    ), "Engineer should not see SSN"
    print("  can_view_field: PASSED")

    docs = [
        {"id": "doc1", "sensitivity": "Public", "content": "Mission statement"},
        {"id": "doc2", "sensitivity": "Confidential", "content": "Salary ranges"},
    ]
    visible = controller.filter_documents("engineer", docs)
    assert (
        len(visible) == 1 and visible[0]["id"] == "doc1"
    ), "Engineer should only see Public doc"
    print("  filter_documents: PASSED")

    # Test RateLimiter
    print("\nTesting RateLimiter...")
    limiter = RateLimiter(max_queries_per_minute=3)
    assert limiter.is_allowed("user1"), "First query should be allowed"
    assert limiter.is_allowed("user1"), "Second query should be allowed"
    assert limiter.is_allowed("user1"), "Third query should be allowed"
    assert not limiter.is_allowed("user1"), "Fourth query should be blocked"
    print("  is_allowed: PASSED")

    # Test CostEnforcer
    print("\nTesting CostEnforcer...")
    enforcer = CostEnforcer()
    assert enforcer.can_afford_query(
        "user1", 50.0
    ), "Should afford $50 within $100 budget"
    enforcer.add_cost("user1", "engineer", 50.0)
    assert enforcer.can_afford_query(
        "user1", 49.0
    ), "Should afford $49 with $50 remaining"
    assert not enforcer.can_afford_query(
        "user1", 51.0
    ), "Should not afford $51 with $50 remaining"
    print("  can_afford_query: PASSED")

    print("\nAll tests passed!")
