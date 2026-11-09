"""FastAPI microservice: SQL Assistant.

Endpoint:
    POST /analyze  {"question": "How are Ahmed Magdy's sales doing?"}
    POST /analyze  {"query": "SELECT ..."}
    POST /run      {"query": "SELECT ..."}   # alias of the skill-driven path

Behavior:
    - Inspects the SQLite schema first.
    - Enforces read-only SELECT (never writes).
    - Returns a structured summary: schema, executed query, columns, rows.

The natural-language -> SQL mapping is the Hermes skill's (agent's) job. This
service is the read-only execution backend the skill drives: given a SELECT, it
validates and runs it, and returns results. It never writes.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from .database import get_connection
from .executor import get_schema, run_query

app = FastAPI(
    title="Fasten_Your_Seat_Belts SQL Assistant",
    version="0.1.0",
    description="Read-only SQLite SQL assistant, ready to wrap in FastAPI.",
)

# Write-command markers: ask the service to reject anything that looks like a
# data-modification or DDL statement in the natural-language path.
_WRITE_MARKERS = ("DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE")
_WRITE_PHRASES = (
    "drop table",
    "delete from",
    "insert into",
    "update ",
    "alter table",
    "create table",
)

# Service-side fallback mapping (NL -> query). The authoritative mapping lives
# in the Hermes skill (agent). This is a self-contained stand-in so the
# service is testable end-to-end without a model.
_INTENT_QUERIES = {
    "total sales": "SELECT SUM(o.amount) AS total_sales, COUNT(*) AS order_count FROM orders o",
    "sales by customer": "SELECT c.name, SUM(o.amount) AS total_spent FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.customer_id ORDER BY total_spent DESC",
    "all customers": "SELECT * FROM customers",
    "all orders": "SELECT * FROM orders",
}

# A question is matched if it contains ANY of the key phrases below.
_KEY_PHRASES = {
    "total sales": ["total", "sum", "sales performance", "revenue"],
    "sales by customer": ["sales by customer", "customer", "spent"],
    "all customers": ["all customers", "customers list"],
    "all orders": ["all orders", "orders list", "list orders"],
}


def _match_intent(question: str) -> str | None:
    q = question.lower()
    for intent, phrases in _KEY_PHRASES.items():
        if any(ph in q for ph in phrases):
            return intent
    return None


class AnalyzeRequest(BaseModel):
    question: str | None = None
    """Natural-language question (the agent/skill resolves this to a SELECT)."""
    query: str | None = None
    """Pre-built read-only SELECT (the skill/agent hands this to the service)."""


class AnalyzeResponse(BaseModel):
    tables: dict
    query: str
    columns: list
    rows: list
    message: str


@app.get("/health")
def health():
    return {"status": "ok", "service": "Fasten_Your_Seat_Belts SQL Assistant"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    conn = get_connection()
    try:
        # --- Skill-driven path: the agent hands us a pre-built SELECT. -----
        if req.query is not None:
            query = req.query.strip()
            cols, rows = run_query(conn, query)
            return AnalyzeResponse(
                tables=get_schema(conn),
                query=query,
                columns=cols,
                rows=rows,
                message="Read-only query executed successfully.",
            )
        # --- Natural-language path (service-side fallback mapping). --------
        if req.question is None:
            raise HTTPException(status_code=400, detail="Provide 'question' or 'query'.")
        if any(marker in req.question.upper() for marker in _WRITE_MARKERS) or any(
            ph in req.question.upper() for ph in _WRITE_PHRASES
        ):
            raise HTTPException(
                status_code=400,
                detail=(
                    "Write commands and data modifications are not allowed. "
                    "Only read-only SELECT queries can be executed."
                ),
            )
        schema = get_schema(conn)
        intent = _match_intent(req.question)
        if intent is None:
            raise HTTPException(
                status_code=400,
                detail=(
                    "I can only answer read-only analytical questions. "
                    "Ask about customers, orders, or sales totals (e.g. "
                    "'total sales', 'customer', 'all orders')."
                ),
            )
        query = _INTENT_QUERIES[intent]
        cols, rows = run_query(conn, query)
        return AnalyzeResponse(
            tables=schema,
            query=query,
            columns=cols,
            rows=rows,
            message="Read-only query executed successfully.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        conn.close()
