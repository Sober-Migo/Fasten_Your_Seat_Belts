"""Gradio web UI for Enterprise SQL Assistant."""

import os
import json
from typing import Optional, List

try:
    import gradio as gr
except ImportError:
    raise RuntimeError("gradio is required. Install with: pip install gradio")


API_BASE_URL = os.environ.get("SQL_ASSISTANT_API_URL", "http://localhost:8000")


def analyze_question(
    question: str,
    history: List[List[Optional[str]]],
    max_results: int = 10,
) -> tuple[List[List[str]], str]:
    if not question.strip():
        return history, "Please enter a question."

    history = history or []
    history.append([question, None])

    try:
        import urllib.request
        payload = json.dumps({"question": question}).encode()
        req = urllib.request.Request(
            f"{API_BASE_URL}/analyze",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())

        response_parts = []
        if data.get("tables"):
            tables_info = "\n".join(f"- {name}: {', '.join(cols)}"
                                   for name, cols in data["tables"].items())
            response_parts.append(f"**Tables:**\n```{tables_info}```\n")

        if data.get("query"):
            response_parts.append(f"**Query:**\n```sql\n{data['query']}\n```\n")

        if data.get("rows"):
            columns = data.get("columns", [])
            rows = data.get("rows", [])
            if columns:
                header = "| " + " | ".join(str(c) for c in columns) + " |"
                sep = "| " + " | ".join("---" for _ in columns) + " |"
                table_rows = []
                for row in rows[:max_results]:
                    cells = [str(cell) if cell is not None else "NULL" for cell in row]
                    table_rows.append("| " + " | ".join(cells) + " |")
                table_body = "\n".join(table_rows)
                response_parts.append(f"**Results ({len(rows)} rows shown):**\n```\n{header}\n{sep}\n{table_body}\n```\n")

        if not response_parts:
            msg = data.get("message", "No results.")
            response_parts.append(msg)

        final_response = "\n".join(response_parts)
        history[-1][1] = final_response

    except Exception as e:
        error_msg = f"\u26a0\ufe0f Error: {str(e)[:500]}"
        history[-1][1] = error_msg

    return history, "\u2705 Done!"


def demo_gradio():
    with gr.Blocks(title="Enterprise SQL Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown("# \U0001f9d1\U0001f4bb Enterprise SQL Assistant\n\nAsk questions about your company data in plain English. Powered by Hermes Agent, FastAPI & Docker.")

        with gr.Row():
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(label="Conversation", height=500, type="messages")
                input_box = gr.Textbox(placeholder="Ask about sales, customers, orders...", lines=2, show_label=False)
                submit_btn = gr.Button("Submit Query", variant="primary")

            with gr.Column(scale=1):
                gr.Markdown("""
### **How it works**

1. Ask a question in English
2. System generates read-only SQL
3. Results shown in formatted tables

**Try asking:**
- "Show all customers"
- "Total sales for all orders"
- "Sales by customer"
- "Orders in October 2026"
""")
                gr.Examples(
                    examples=[
                        ["Show all customers"],
                        ["Total sales for all orders"],
                        ["Sales by customer name"],
                        ["Orders placed in October 2026"],
                    ],
                    inputs=input_box,
                )

        submit_btn.click(fn=analyze_question, inputs=[input_box, chatbot], outputs=[chatbot, gr.Textbox(label="Status")])
        input_box.submit(fn=analyze_question, inputs=[input_box, chatbot], outputs=[chatbot, gr.Textbox(label="Status")])

    app.launch(server_name="0.0.0.0", server_port=7860, share=False)


if __name__ == "__main__":
    demo_gradio()
