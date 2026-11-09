# 01_hermes_sql_agent

Enterprise SQL Assistant powered by Hermes Agent. Safely analyzes SQLite databases using a custom read-only `sql-db-analyzer` skill.

## Structure

```text
01_hermes_sql_agent/
├── skills/
│   └── sql_db_analyzer/
│       └── SKILL.md
├── database/
│   └── sample_company.db
├── tests/
│   └── test_queries.py
└── README.md
```

## Quick start

1. Generate the sample database:

   ```bash
   python 01_hermes_sql_agent/database/setup_db.py
   ```

2. Run the regression tests:

   ```bash
   cd 01_hermes_sql_agent
   python -m pytest tests/test_queries.py -v
   # or plain:
   python tests/test_queries.py
   ```

3. Launch the agent with the skill:

   ```bash
   hermes "Analyze the sales performance for customer Ahmed Magdy using the sql-db-analyzer skill."
   ```

## Skill contract

- Inspects schema first.
- Executes only `SELECT` queries.
- Validates safety before running.
- Returns clean tabular summaries.

## Tests

`tests/test_queries.py` covers:
- tables exist (`customers`, `orders`),
- customers row set,
- orders aggregate (`SUM` = 7350.0, count = 4),
- customers/orders join ordering.

Run all with `python tests/test_queries.py` from `01_hermes_sql_agent/`.
