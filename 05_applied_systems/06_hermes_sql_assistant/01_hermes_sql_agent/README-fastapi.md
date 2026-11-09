# SQL Assistant — FastAPI service

Self-contained read-only SQLite SQL assistant. Run it with:

```bash
cd 01_hermes_sql_agent

# 1) (optional) install dependencies in a venv
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) start the service
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Then test it with any HTTP client:

```bash
# health check
curl http://localhost:8000/health

# a read-only analytical question
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the total sales and order count?"}' | python -m json.tool

# a question the service can't answer -> 400
curl -s -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "DROP TABLE customers"}' | python -m json.tool
```

Expected responses:

- `GET /health` -> `{"status":"ok","service":"..."}`
- `POST /analyze` with a supported question -> JSON containing `schema`, `query`, `columns`, `rows`.
- `POST /analyze` with a write/non-SELECT question -> `400` with a clear "rejected" message.

The same `app/executor.py` + `01_hermes_sql_agent/tests/test_queries.py` regression suite is what keeps the read-only guarantee intact.

---

### Docker

```bash
# build
docker build -t sql-assistant .

# run
docker run --rm -p 8000:8000 sql-assistant

# or with docker-compose
docker compose up --build
```

`GET /health` is the fastest way to confirm the container is serving.
