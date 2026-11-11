"""Standalone Gradio UI for Enterprise SQL Assistant optimized for Hugging Face Spaces.

Embeds SQLite directly (no FastAPI needed). Just copy gradio_ui.py + sample_company.db
to any HF Space and run `python gradio_ui.py`.
"""

import os
import re
import sqlite3
from typing import Optional, List, Dict, Any

try:
    import gradio as gr
except ImportError:
    gr = None  # Not running in a Gradio context

# Import spaces.GPU decorator (for HF zero-GPU)
try:
    from gradio.spaces import GPU
except ImportError:
    GPU = lambda *a, **kw: lambda f: f  # no-op when not in HF space

# Configuration
DB_PATH = os.environ.get("SQL_DB_PATH", "sample_company.db")

READ_ONLY_BLOCKERS = [
    "DROP", "DELETE", "UPDATE", "INSERT", "PRAGMA",
    "ATTACH", "REPLACE", "CREATE", "ALTER", "GRANT",
    "REVOKE", "TRUNCATE", "EXPLAIN", "ANALYZE",
]


def validate_query(query):
    """Check if query is safe read-only SELECT."""
    cleaned = re.sub(r"--.*$", "", query, flags=re.MULTILINE).strip().upper()
    words = [w.strip("(),;:") for w in cleaned.split()]
    for word in words:
        if word in READ_ONLY_BLOCKERS:
            return False, f"Forbidden operation: {word}"
    return True, "Safe"


def execute_query(query):
    """Execute a read-only SQL query against the sample database."""
    conn = sqlite3.connect(DB_PATH)
    try:
        cleaned = query.strip().rstrip(";").strip()
        cu = cleaned.upper()
        if not cu.startswith("SELECT"):
            return [], [], "\u26a0\ufe0f Only SELECT queries allowed."
        words = [w.strip("(),;:") for w in cu.split()]
        for word in words:
            if word in READ_ONLY_BLOCKERS:
                return [], [], f"\u26a0\ufe0f Forbidden: {word}"
        cursor = conn.execute(cleaned)
        rows = cursor.fetchall()
        columns = [d[0] for d in cursor.description] if cursor.description else []
        result = ""
        if columns and rows:
            h = "| " + " | ".join(columns) + " |"
            s = "| " + " | ".join(["---"] * len(columns)) + " |"
            rl = ["| " + " | ".join(str(c or "NULL") for c in r) + " |" for r in rows]
            result = "\n".join([h, s] + rl)
        return columns, rows, result
    finally:
        conn.close()


@GPU(duration=60)
def answer_question(question):
    """Process natural language question -> generate SQL -> execute -> format."""
    if not question.strip():
        return "Please enter a question."

    ql = question.lower()
    sql_map = {
        "total sales":      "SELECT SUM(amount) AS total_sales FROM orders",
        "sales by customer": (
            "SELECT c.name, SUM(o.amount) AS total "
            "FROM customers c JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.name ORDER BY total DESC"
        ),
        "all customers":   "SELECT * FROM customers",
        "all orders":      "SELECT * FROM orders",
        "october":         "SELECT * FROM orders WHERE order_date LIKE '2026-10%'",
        "november":        "SELECT * FROM orders WHERE order_date LIKE '2026-11%'",
        "egypt":           "SELECT * FROM customers WHERE country = 'Egypt'",
        "usa":             "SELECT * FROM customers WHERE country = 'USA'",
        "uk":              "SELECT * FROM customers WHERE country = 'UK'",
        "ahmed magdy":     "SELECT * FROM customers WHERE name LIKE '%Ahmed%' AND name LIKE '%Magdy%'",
    }

    best_q, best_s = None, 0
    for k, v in sql_map.items():
        score = sum(1 for word in k.split() if word in ql)
        if score > best_s:
            best_s, best_q = score, v

    gen_query = best_q if best_q and best_s > 0 else "SELECT * FROM orders LIMIT 5"
    columns, rows, tbl = execute_query(gen_query)

    resp = f"**Question:** {question}\n\n"
    resp += f"**Generated Query:**\n```sql\n{gen_query}\n```\n\n"
    resp += f"**Results:**\n```\n{tbl}\n```\n" if tbl else "*No results returned.*\n"
    return resp


def process_message(message, history):
    """Handle chat messages."""
    if not message.strip():
        return history, ""
    history = history or []
    history.append({"role": "user", "content": message})
    try:
        response = answer_question(message)
    except Exception as e:
        response = f"Error:\n\nDetails: `{str(e)[:300]}`"
    history.append({"role": "assistant", "content": response})
    return history, ""


def demo_gradio():
    """Launch the Gradio application for Hugging Face Spaces."""
    if gr is None:
        print("gradio not installed — skipping UI launch.")
        return

    with gr.Blocks(title="Enterprise SQL Assistant", theme=gr.themes.Soft(primary_hue="blue")) as app:
        gr.Markdown(
            "# Enterprise SQL Assistant\n"
            "Ask questions about company data in plain English.\n\n"
            "**Schema:** `customers(id,name,country)` \u00b7 `orders(id,customer_id,amount,order_date)`"
        )
        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(label="Conversation", height=450, type="messages")
                inp = gr.Textbox(
                    placeholder="Ask about sales, customers, orders\u2026",
                    lines=2,
                    show_label=False,
                )
                btn = gr.Button("Submit Query", variant="primary")
            with gr.Column(scale=1):
                gr.Markdown(
                    "### How it works\n\n"
                    "1. Ask a question\n2. System generates read-only SQL\n"
                    "3. Results shown in tables\n\n"
                    "**Try:**\n"
                    "- \"Show all customers\"\n"
                    "- \"Total sales for all orders\"\n"
                    "- \"Sales by customer\"\n"
                    "- \"Orders in October 2026\""
                )
                gr.Examples(
                    examples=[
                        ["Show all customers"],
                        ["Total sales for all orders"],
                        ["Sales by customer name"],
                        ["Orders placed in October 2026"],
                        ["Customers from Egypt"],
                        ["Sales by customer"],
                    ],
                    inputs=inp,
                )
        btn.click(fn=process_message, inputs=[inp, chatbot], outputs=[chatbot, inp])
        inp.submit(fn=process_message, inputs=[inp, chatbot], outputs=[chatbot, inp])

    app.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    demo_gradio()
