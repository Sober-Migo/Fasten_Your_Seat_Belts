# Fasten_Your_Seat_Belts

Repo for the first practical step in the "Fasten Your Seat Belts" journey: building an
**Enterprise SQL Assistant using Hermes Agent**.

## Contents

- `01_hermes_sql_agent/` — SQL Assistant skill + sample SQLite DB + read-only regression tests.
- `README.md` — this file.

## Quick start

```bash
# 1) Build the sample SQLite database
python 01_hermes_sql_agent/database/setup_db.py

# 2) Verify the skill + schema detectors
python 01_hermes_sql_agent/tests/test_queries.py

# 3) Hand it to Hermes Agent
hermes "Analyze the sales performance for customer Ahmed Magdy using the sql-db-analyzer skill."
```

Setup DB is a one-off generator. The schema it creates is locked in
`01_hermes_sql_agent/database/sample_company.db`.

## Next steps

- Wrap the agent in a FastAPI microservice for an enterprise product.
- Add a Docker environment to isolate database execution.
