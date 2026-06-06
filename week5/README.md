# Week 5 — Agent Architecture with LLM Tool Use

## Overview

This week you'll build an AI agent that answers TechCorp business questions by combining an LLM with database queries and document retrieval. The agent will:

- Use Gemini 2.5 Pro to reason about which tools to call
- Query the TechCorp SQLite database (employees, expenses, projects, benefits)
- Track API costs and enforce access control
- Handle errors gracefully

**Key concept:** Agents chain together LLM reasoning + tool execution. The LLM decides which tools to call, you handle the results, then synthesize an answer.

---

## Setup

### 1. Get a Google AI API Key

Visit [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) and generate a free API key.

```bash
# Set as environment variable
export GOOGLE_API_KEY="AIza..."

# Or create .env file in week5/
echo "GOOGLE_API_KEY=AIza..." > .env
```

### 2. Install Dependencies

```bash
cd week5
pip install -r requirements.txt
```

**Required packages:**

- `google-genai` - Google's Gemini API

---

## Your Tasks

### Task 1. Read and Understand the Tool Base Class

Open `app_starter.py`. Understand that the `execute()` method works on the Tool base class:

```python
class Tool:
    """Base class for tools the agent can call."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def execute(self, **kwargs) -> str:
        # TODO: This is implemented by subclasses.
        # Each subclass should override this method.
        raise NotImplementedError
```

The `Tool` class is the foundation for all tools the agent can call. Every tool has a `name`, a `description`, and an `execute()` method. The `raise NotImplementedError` ensures that any subclass that forgets to implement `execute()` will fail loudly rather than silently.

### Task 2. Implement EmployeeLookupTool

Implement `execute()` on `EmployeeLookupTool` to look up employees from the SQLite database:

```python
class EmployeeLookupTool(Tool):
    def execute(self, employee_name: str = None, employee_id: str = None) -> str:
        # TODO:
        # 1. Connect to SQLite database at self.db_path
        # 2. If employee_id provided: SELECT * FROM employees WHERE id = ?
        # 3. If employee_name provided: SELECT * FROM employees WHERE name LIKE ?
        # 4. Convert results to JSON and return
        # 5. If no results, return "Employee not found"
```
The tool accepts either a name (partial match) or an ID (exact match). Use Python's built-in sqlite3 module — no extra dependencies needed. Below is the basic pattern for querying SQLite — how to open a connection, create a cursor, run a query, fetch the results, and close the connection. This is for reference only, it is not sufficient to run this function.

```python
conn = sqlite3.connect(self.db_path)
cursor = conn.cursor()
cursor.execute("SELECT * FROM employees WHERE name LIKE ?", (f"%{name}%",))
rows = cursor.fetchall()
conn.close()
```

### Task 3. Implement PolicySearchTool

Implement `PolicySearchTool` to search policy documents by keyword. Start by inspecting the `data/` folder to identify the documents you need to read in. Definitely read the `documents.json` file.

```python
class PolicySearchTool(Tool):
    def __init__(self):
        super().__init__(
            "policy_search",
            "Search policy documents by keyword or topic"
        )
        # TODO: Load documents

    def execute(self, query: str, limit: int = 5) -> str:
        # TODO: Implement policy search:
        # 1. Load documents (from JSON file in data/ folder)
        # 2. Search documents by keyword match
        # 3. Return top-N matching documents
        # 4. Include title and snippet (first 500 chars) for each
```

Below are hints to write the code for this chunk, although you don't strictly need to adhere to these. If you change the logic of your functions significantly, these might not work.

- Load the documents in `__init__` so they are only read from disk once:
    ```python
    with open("data/documents.json") as f:
        self.documents = json.load(f)
    ```
- For the keyword search, a simple case-insensitive string match may be sufficient:
    ```python
    matches = [doc for doc in self.documents if query.lower() in doc["content"].lower()]
    ```

### Task 4. Implement ExpenseQueryTool

Implement `ExpenseQueryTool` to look up expense approval limits by role from `data/policies.json`:

```python
class ExpenseQueryTool(Tool):
    def __init__(self):
        super().__init__(
            "expense_query",
            "Query expense approval limits by role"
        )
        # TODO: Load policies from data/policies.json

    def execute(self, role: str) -> str:
        # TODO:
        # 1. Look up role in self.policies["expense"]["approval_limits"]
        # 2. Return: "Approval limit for {role}: ${amount}"
        # 3. If role not found, return "Role not found: {role}"
```

Valid roles are: `ic1_ic2`, `ic3`, `manager`, `director`, `vp`. Example output:

```markdown
Approval limit for manager: $5000
```

### Task 5. Implement the Agent Class

The Agent class ties everything together. **This is the section where you will most likely need to re-check the logic to ensure consistency in your code. You must ensure that the work you did in previous tasks gets called and used correctly using this class. Do not rely solely on the code provided. Feel free to change the structure of this as well as other code chunks.** Play around with your agent!

Below is a description of the four methods in the provided code based on which you can develop further:

#### Method 1. `__init__` — set up the agent:

```python
def __init__(self, db_path: str, api_key: str = None):
    # TODO:
    # 1. Initialize Google GenAI client:
    #    self.client = genai.Client(api_key=self.api_key)
    # 2. Initialize tools dictionary:
    #    self.tools = {
    #        "employee_lookup": EmployeeLookupTool(db_path),
    #        "policy_search": PolicySearchTool(),
    #        "expense_query": ExpenseQueryTool(),
    #    }
    # 3. Initialize tracking variables:
    #    self.token_count = 0
    #    self.total_cost = 0.0
    #    self.queries_run = 0
```

#### Method 2. `_build_system_prompt` — describe the available tools to the LLM using a System Prompt:

```python
def _build_system_prompt(self, user_role: str) -> str:
    # TODO: Return a prompt string that:
    # 1. Describes the agent's purpose (answering TechCorp business questions)
    # 2. Lists each tool by name and description
    # 3. Tells the LLM to indicate which tool to call and with what arguments
    # 4. Includes the user's role as context
```
This is where routing happens: during deployment, Gemini will use information in the System Prompt to decide which tool needs to be used to respond to the user's input. In a sense, Gemini will "translate" the user's input into the logic with which our agent can work. 

Here, Gemini reads your tool descriptions and matches them to the user's question — if your description of `expense_query` says "Query expense approval limits by role", Gemini will call it when a user asks "What's the spending limit for a manager?" and pass role="manager". Write clear, specific descriptions.

**Example-only** prompt structure:
```markdown
You are a TechCorp assistant. Answer employee questions using the tools below.
User role: engineer

Available tools:
- employee_lookup: Find employee information by name or ID
- policy_search: Search policy documents by keyword or topic
- expense_query: Query expense approval limits by role (engineer, manager, director, vp)

To use a tool, respond with:
TOOL: <tool_name>
ARGS: <argument>=<value>
```
#### Method 3. `query` — the main reasoning loop:

```python
def query(self, user_query: str, user_role: str = "engineer") -> Dict:
    # TODO: Implement the reasoning loop
    # 1. Call _build_system_prompt(user_role) to build the system prompt

    # 2. Call Gemini LLM with system prompt + user question
    #     - self.client.models.generate_content(model="gemini-2.5-pro", ...)

    # 3. Parse LLM response to identify tool calls
    #     - Check if response mentions any tool names
    #     - Extract parameters from response

    # 4. Execute tools with extracted parameters
    #     - tool.execute() with parameters
    #     - Collect results

    # 5. Synthesize final answer
    #     - Pass tool results back to LLM
    #     - Get final answer

    # 6. Track tokens and cost
    #    - Count tokens in request/response
    #    - Calculate cost: (tokens / 1_000_000) * rate
    #    - Update totals
```

As described in the TODO steps, you must come up with logic that ties all parts of your code together to process each user prompt, generate output, and measure the cost of the agent's operation. There are many ways to build this logic. **Below is an example of such logic, though you are encouraged to come up with a more robust and efficient reasoning loop for your agent. Note that this has additional steps as compared to the docstring from `app_starter.py`. This is just an example, and your logic might also need more or different steps.**

- You have built a system prompt describing the tools available to the LLM (you have also written the code for these tools)
- Gemini reads the user's question and uses the system prompt to decide which tool to call
- You parse Gemini's response to extract the tool name and arguments
- You call that tool with the extracted arguments and get real data back
- You pass the tool result back to Gemini to produce a final answer
- You count tokens across both LLM calls and calculate the total cost

You can use Method 4 below for the cost calculations.

#### Method 4. `get_metrics` — return running totals:

```python
def get_metrics(self) -> Dict:
    # TODO: Return:
    # - total_queries: self.queries_run
    # - total_tokens: self.token_count
    # - total_cost: self.total_cost
    # - avg_cost_per_query: self.total_cost / self.queries_run
    #   (return 0.0 if no queries have been run yet)
```

### Task 6. Test Your Implementation

Run the built-in test block to verify your agent works end-to-end:

```bash
cd week5
python3 app_starter.py
```

You should see output that's something like this. This is a hypothetical sample and not a source of truth:

```markdown
Agent initialized successfully

Testing query: 'What is the travel policy?'
Answer: The TechCorp travel policy requires all business travel to be pre-approved...
Tokens: 1243
Cost: $0.000432

Metrics: {'total_queries': 1, 'total_tokens': 1243, 'total_cost': 0.000432, 'avg_cost_per_query': 0.000432}
```

If you see `TODO: implement agent query logic`, your `query()` method is not yet implemented. If you see an error, check TROUBLESHOOTING.md.

---

## Data & Database

The TechCorp SQLite database (`data/techcorp.db`) contains:

**Tables:**

- `employees` - id, name, email, department_id, department_name, job_level, title, salary, ssn, address, phone, hire_date, manager_id, bonus_eligible, stock_options
- `expenses` - id, employee_id, employee_name, amount, category, description, date, status, approver_id, approver_name, vendor, receipt_location, notes
- `projects` - id, name, description, budget, spent, status, start_date, end_date, lead_id, lead_name, team_ids, team_size, department_id
- `benefits` - employee_id, employee_name, health_plan, health_plan_cost, dental_plan, vision_plan, retirement_plan, retirement_contribution_pct, life_insurance, fsa_balance, hsa_balance, pto_days, pto_used

**Your tools will query these tables.** Example:

```python
import sqlite3

def employee_lookup(name):
    conn = sqlite3.connect("data/techcorp.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM employees WHERE name LIKE ?", (f"%{name}%",))
    rows = cursor.fetchall()
    conn.close()
    return rows
```

---
### Access Control

The `data/access_control.json` file defines the role-based access control rules for the TechCorp system. It specifies what each user role is permitted to see and do, as well as which data fields are considered sensitive (e.g. salary, ssn, address).

You don't need to enforce these rules in Week 5 — the `user_role` parameter in `Agent.query()` is accepted but not yet used. Week 6 will build on your agent foundation to enforce these permissions. For now, feel free to read through this file to understand the access model you'll be implementing.


---

## Cost Tracking

Gemini 2.5 Pro pricing (free tier included):

- Input: $0.075 per 1M tokens
- Output: $0.3 per 1M tokens

The Agent class automatically calculates:

```python
def _estimate_query_cost(input_tokens, output_tokens):
    input_cost = (input_tokens / 1_000_000) * 0.075
    output_cost = (output_tokens / 1_000_000) * 0.3
    return input_cost + output_cost

# After each query:
metrics = agent.get_metrics()
print(f"Total queries: {metrics['total_queries']}")
print(f"Total cost: ${metrics['total_cost']:.4f}")
print(f"Avg cost per query: ${metrics['avg_cost_per_query']:.4f}")
```

---

## Deliverables

1. **`app_starter.py`** — Agent class with 3+ tools, tool execution loop, cost tracking
2. **One report with screenshots and documentation if necessary** — 10 test queries showing working agent + total cost, description of code structure if it was modified significantly

## Grading

| Criterion | Weight |
|-----------|--------|
| Tools implemented in code (3+ with execute()) | 30% |
| Agent reasoning loop code (LLM calls tools correctly) | 30% |
| Cost tracking code (accurate token/cost calculation) | 20% |
| Report showing tests passing (screenshots of tools + agent responding) | 20% |

---

## Common Issues

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## Next Week

Week 6 will add access control and rate limiting. Build a solid agent foundation this week!
