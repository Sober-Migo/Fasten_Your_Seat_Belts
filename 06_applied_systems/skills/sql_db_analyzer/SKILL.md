---
name: sql-db-analyzer
description: Inspects SQLite database schemas, validates query safety, executes read-only SQL queries, and summarizes analytical data.
---

# SQL Database Analyzer Skill

## Overview
This skill enables the agent to safely connect to an SQLite database, inspect table schemas, construct valid read-only SQL queries from natural-language requests, and return clean analytical summaries.

## Core Directives & Rules
1. ALWAYS inspect the database schema first before writing any query.
2. ONLY execute read-only queries (`SELECT`). Never execute `DROP`, `DELETE`, `UPDATE`, or `INSERT`.
3. Validate every generated query against the inspected schema before execution.
4. Format output data clearly using tables or bullet points.
5. If a request cannot be satisfied by read-only queries, say so explicitly instead of guessing.

## Execution Steps

### Step 1: Inspect Schema
Inspect the schema via the FastAPI service so the agent sees the same tables the service will query. Confirm the service is up with a health check, then mirror the local schema if needed:

```bash
curl -s http://localhost:8000/health
python -c "import sqlite3; conn=sqlite3.connect('01_hermes_sql_agent/database/sample_company.db'); print(conn.execute(\"SELECT sql FROM sqlite_master WHERE type='table';\").fetchall()); conn.close()"
```

### Step 2: Build the Query
Construct a read-only `SELECT` statement that answers the user's natural-language request. Translating natural language to SQL is the agent's job; keep the query read-only.

### Step 3: Validate Query Safety
Check the generated `SELECT` against the schema captured in Step 1. Confirm:
- All referenced tables exist.
- All referenced columns exist.
- Only `SELECT` statements are used.

### Step 4: Execute via Service
Call the FastAPI service to execute the validated query and fetch results:

```bash
curl -s -X POST http://localhost:8000/analyze   -H "Content-Type: application/json"   -d "{\"query\": \"<the read-only SQL>\"}" | python -m json.tool
```

The response contains `tables`, `query`, `columns`, `rows`, and `message`.

### Step 5: Summarize
Format the results as a clear table or bullet points and include a short written summary.

## Example
**User:** "Analyze the sales performance for customer Ahmed Magdy."

**Agent:**
1. Inspects schema (customers, orders tables).
2. Validates query:
   ```sql
   SELECT * FROM customers c
   JOIN orders o ON c.customer_id = o.customer_id
   WHERE c.name = 'Ahmed Magdy';
   ```
3. Executes the query and returns results as a table + summary.

## Folder Convention
- `01_hermes_sql_agent/database/sample_company.db` — SQLite sample database.
- `01_hermes_sql_agent/tests/test_queries.py` — read-only query regression tests.
