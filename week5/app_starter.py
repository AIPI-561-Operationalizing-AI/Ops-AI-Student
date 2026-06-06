"""
Week 5: Agent Architecture Starter Template

Build an AI agent that answers TechCorp questions using:
- Gemini 2.5 Pro LLM (free tier via Google AI API)
- SQLite database queries
- Policy document retrieval

Complete the TODO sections marked below.
"""

import json
import sqlite3
from typing import Dict, Any
import google.genai as genai
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")


# TASK 1: Implement the Tool base class


class Tool:
    """Base class for tools the agent can call."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> str:
        """Execute the tool.

        TODO: This is implemented by subclasses.
        Each subclass should override this method.
        """
        raise NotImplementedError


# TASK 2: Implement EmployeeLookupTool


class EmployeeLookupTool(Tool):
    """Look up employee information from SQLite database."""

    def __init__(self, db_path: str):
        super().__init__("employee_lookup", "Find employee information by name or ID")
        self.db_path = db_path

    def execute(self, employee_name: str = None, employee_id: str = None) -> str:
        """Look up employee by name or ID.

        TODO: Query the employees table:
        1. Connect to SQLite database at self.db_path
        2. If employee_id is provided:
           - SELECT * FROM employees WHERE id = ?
        3. If employee_name is provided:
           - SELECT * FROM employees WHERE name LIKE ?
        4. Convert results to JSON and return
        5. If no results found, return "Employee not found"

        Args:
            employee_name: Name to search for (partial match ok)
            employee_id: ID to search for (exact match)

        Returns:
            JSON string with employee info or error message
        """
        try:
            # TODO: implement
            return "TODO: implement employee lookup"
        except Exception as e:
            logger.error(f"Employee lookup error: {e}")
            return f"Error: {str(e)}"


# TASK 3: Implement PolicySearchTool


class PolicySearchTool(Tool):
    """Search policy documents by keyword."""

    def __init__(self):
        super().__init__("policy_search", "Search policy documents by keyword or topic")
        # TODO: Load data/documents.json
        self.documents = []

    def execute(self, query: str, limit: int = 5) -> str:
        """Search policies by keyword.

        TODO: Implement policy search:
        1. Load documents (from JSON file in data/ folder)
        2. Search documents by keyword match
        3. Return top-N matching documents
        4. Include title and snippet (first 500 chars) for each

        Args:
            query: Search term
            limit: Max results to return

        Returns:
            Formatted string with matching documents
        """
        try:
            # TODO: implement
            return "TODO: implement policy search"
        except Exception as e:
            logger.error(f"Policy search error: {e}")
            return f"Error: {str(e)}"


# TASK 4: Implement ExpenseQueryTool


class ExpenseQueryTool(Tool):
    """Query expense policies and approval limits."""

    def __init__(self):
        super().__init__("expense_query", "Query expense approval limits by role")
        # TODO: load data/policies.json into the documents attribute
        self.policies = {}

    def execute(self, role: str) -> str:
        """Query expense approval limit for a given role.

        TODO: Implement expense lookup:
        1. Look up role in self.policies["expense"]["approval_limits"]
        2. Return: "Approval limit for {role}: ${amount}"
        3. If role not found, return "Role not found: {role}"

        Args:
            role: Employee role (ic1_ic2, ic3, manager, director, vp)

        Returns:
            String with approval limit for the given role
        """
        try:
            # TODO: implement
            return "TODO: implement expense query"
        except Exception as e:
            logger.error(f"Expense query error: {e}")
            return f"Error: {str(e)}"


# TASK 5: Implement the Agent class


class Agent:
    """AI agent that answers questions using Gemini LLM + tools."""

    def __init__(self, db_path: str, api_key: str = None):
        """Initialize the agent.

        TODO:
        1. Get API key from parameter or GOOGLE_API_KEY environment variable
        2. Raise ValueError if no API key provided
        3. Initialize Google GenAI client with api_key
        4. Initialize all tools (EmployeeLookup, PolicySearch, ExpenseQuery)
        5. Initialize token and cost tracking variables

        Args:
            db_path: Path to SQLite database
            api_key: Google AI API key (or use GOOGLE_API_KEY env var)
        """
        self.db_path = db_path
        self.api_key = api_key or GOOGLE_API_KEY

        if not self.api_key:
            raise ValueError(
                "GOOGLE_API_KEY not set. Get free key at: "
                "https://aistudio.google.com/app/apikey"
            )

        # TODO: Initialize Google GenAI client
        # self.client = genai.Client(api_key=self.api_key)

        # TODO: Initialize tools dictionary
        # self.tools = {
        #     "employee_lookup": EmployeeLookupTool(db_path),
        #     "policy_search": PolicySearchTool(),
        #     "expense_query": ExpenseQueryTool(),
        # }

        # TODO: Initialize metrics
        # self.token_count = 0
        # self.total_cost = 0.0
        # self.queries_run = 0

    def _build_system_prompt(self, user_role: str) -> str:
        """Build system prompt describing available tools.

        TODO: Create a prompt that:
        1. Describes the agent's purpose
        2. Lists all available tools with descriptions
        3. Explains how to use them
        4. Sets the user's role context

        Returns:
            System prompt string
        """
        # TODO: implement
        return "TODO: implement system prompt"

    def query(self, user_query: str, user_role: str = "engineer") -> Dict[str, Any]:
        """Answer a question using LLM + tools.

        TODO: Implement the reasoning loop:

        1. Call _build_system_prompt(user_role) to build the system prompt

        2. Call Gemini LLM with system prompt + user question
           - self.client.models.generate_content(model="gemini-2.5-pro", ...)

        3. Parse LLM response to identify tool calls
           - Check if response mentions any tool names
           - Extract parameters from response

        4. Execute tools with extracted parameters
           - tool.execute() with parameters
           - Collect results

        5. Synthesize final answer
           - Pass tool results back to LLM
           - Get final answer

        6. Track tokens and cost
           - Count tokens in request/response
           - Calculate cost: (tokens / 1_000_000) * rate
           - Update totals

        Args:
            user_query: The question to answer
            user_role: User's role (for access control in future weeks)

        Returns:
            Dict with keys:
            - "answer": str - the response
            - "tokens_used": int - total tokens
            - "cost": float - cost in dollars
            - "role": str - user role
        """
        logger.info(f"Processing query: {user_query}")

        # TODO: implement agent query logic

        return {
            "answer": "TODO: implement agent query logic",
            "tokens_used": 0,
            "cost": 0.0,
            "role": user_role,
        }

    def _estimate_query_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on tokens.

        Gemini 2.5 Pro pricing:
        - Input: $0.075 per 1M tokens
        - Output: $0.3 per 1M tokens
        """
        input_cost = (input_tokens / 1_000_000) * 0.075
        output_cost = (output_tokens / 1_000_000) * 0.3
        return input_cost + output_cost

    def get_metrics(self) -> Dict[str, Any]:
        """Return performance metrics.

        TODO: Return dict with:
        - total_queries: number of queries processed
        - total_tokens: cumulative tokens used
        - total_cost: cumulative cost in dollars
        - avg_cost_per_query: average cost per query
        """
        # TODO: implement
        return {
            "total_queries": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "avg_cost_per_query": 0.0,
        }


# TASK 6: Test your implementation

if __name__ == "__main__":
    """Quick test of agent functionality."""
    import sys

    try:
        # Initialize agent
        agent = Agent("data/techcorp.db")
        print("Agent initialized successfully")

        # Test a query
        print("\nTesting query: 'What is the travel policy?'")
        result = agent.query("What is the travel policy?")
        print(f"Answer: {result['answer']}")
        print(f"Tokens: {result['tokens_used']}")
        print(f"Cost: ${result['cost']:.6f}")

        # Check metrics
        metrics = agent.get_metrics()
        print(f"\nMetrics: {metrics}")

    except Exception as e:
        print(f"Error: {e}")
        logger.exception("Error during test")
        sys.exit(1)
