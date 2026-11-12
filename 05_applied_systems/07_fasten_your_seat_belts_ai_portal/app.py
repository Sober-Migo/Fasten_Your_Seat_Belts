import os
import sqlite3
import threading
from pathlib import Path

import gradio as gr
import spaces
from dotenv import load_dotenv

load_dotenv()

CUSTOMERS = [
    (1, "Ahmed Magdy", "Egypt"),
    (2, "John Doe", "USA"),
    (3, "Sarah Connor", "UK"),
]
ORDERS = [
    (101, 1, 1500.0, "2026-10-01"),
    (102, 1, 2300.0, "2026-10-15"),
    (103, 2, 450.0, "2026-10-20"),
    (104, 3, 3100.0, "2026-11-01"),
]
SQL_MAP = {
    "total sales": "SELECT SUM(amount) AS total_sales FROM orders",
    "sales by customer": "SELECT c.name, SUM(o.amount) AS total FROM customers c JOIN orders o ON c.customer_id = o.customer_id GROUP BY c.name ORDER BY total DESC",
    "all customers": "SELECT * FROM customers",
    "all orders": "SELECT * FROM orders",
    "october": "SELECT * FROM orders WHERE order_date LIKE '2026-10%'",
    "november": "SELECT * FROM orders WHERE order_date LIKE '2026-11%'",
    "egypt": "SELECT * FROM customers WHERE country = 'Egypt'",
    "usa": "SELECT * FROM customers WHERE country = 'USA'",
    "uk": "SELECT * FROM customers WHERE country = 'UK'",
    "ahmed magdy": "SELECT * FROM customers WHERE name LIKE '%Ahmed%' AND name LIKE '%Magdy%'",
}

SENTIMENT_MODEL = os.getenv(
    "SENTIMENT_MODEL", "distilbert/distilbert-base-uncased-finetuned-sst-2-english"
)
_sentiment_pipeline = None
_sentiment_pipeline_lock = threading.Lock()


def _get_sentiment_pipeline():
    global _sentiment_pipeline
    if _sentiment_pipeline is None:
        with _sentiment_pipeline_lock:
            if _sentiment_pipeline is None:
                from transformers import pipeline

                _sentiment_pipeline = pipeline(
                    "sentiment-analysis", model=SENTIMENT_MODEL, device=-1
                )
    return _sentiment_pipeline


def _generate_sql(question: str) -> str:
    normalized = question.lower()
    best_sql = None
    best_length = 0
    for phrase, sql in SQL_MAP.items():
        words = phrase.split()
        if len(words) > best_length and all(word in normalized for word in words):
            best_sql, best_length = sql, len(words)
    return best_sql or "SELECT * FROM orders LIMIT 5"


def _markdown_table(columns, rows) -> str:
    if not rows:
        return "No rows returned."

    def escape(value):
        return str(value).replace("|", "\\|").replace("\n", " ")

    header = "| " + " | ".join(escape(column) for column in columns) + " |"
    divider = "| " + " | ".join("---" for _ in columns) + " |"
    body = ["| " + " | ".join(escape(value) for value in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def answer_sql(question: str):
    if not question or not question.strip():
        return "", "Please enter a question."
    sql = _generate_sql(question.strip())
    connection = sqlite3.connect(":memory:")
    try:
        connection.executescript(
            "CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT NOT NULL, country TEXT NOT NULL);"
            "CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, amount REAL, order_date TEXT);"
        )
        connection.executemany("INSERT INTO customers VALUES (?, ?, ?)", CUSTOMERS)
        connection.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ORDERS)
        result = connection.execute(sql)
        return sql, _markdown_table([column[0] for column in result.description], result.fetchall())
    except sqlite3.Error as error:
        return sql, f"Query failed: {error}"
    finally:
        connection.close()


def _rag_retriever(file_path: str):
    from chromadb.utils import embedding_functions
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_community.vectorstores import Chroma
    from langchain_core.embeddings import Embeddings
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    class ChromaDefaultEmbeddings(Embeddings):
        def __init__(self):
            self._function = embedding_functions.DefaultEmbeddingFunction()

        def embed_documents(self, texts):
            return self._function(texts)

        def embed_query(self, text):
            return self._function([text])[0]

    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"PDF not found: {path}")
    documents = PyPDFLoader(str(path)).load()
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "100")),
        length_function=len,
        separators=["\n\n", "\n", " ", ""],
    ).split_documents(documents)
    store = Chroma.from_documents(documents=chunks, embedding=ChromaDefaultEmbeddings())
    return store.as_retriever(search_kwargs={"k": 4})


def _extractive_answer(retriever, question: str) -> str:
    documents = retriever.invoke(question)
    if not documents:
        return "No relevant passages found in the document."
    passages = [f"[Passage {index + 1}]\n{doc.page_content.strip()}" for index, doc in enumerate(documents)]
    return "(Extractive mode — no LLM)\n\nMost relevant passages:\n\n" + "\n\n---\n\n".join(passages)


def answer_rag(file_path: str, question: str) -> str:
    if not file_path:
        return "Please upload a PDF first."
    if not question or not question.strip():
        return "Please enter a question about the document."

    retriever = _rag_retriever(file_path)
    query = question.strip()
    key = os.getenv("GROQ_API_KEY")
    if not key:
        return _extractive_answer(retriever, query)

    try:
        from groq import Groq

        context = "\n\n".join(doc.page_content for doc in retriever.invoke(query))
        response = Groq(api_key=key).chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.1-8b-instant"),
            messages=[
                {"role": "system", "content": "Answer using only the supplied context. If the answer is not present, say you do not know. Be concise and factual."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"},
            ],
            max_tokens=int(os.getenv("MAX_NEW_TOKENS", "256")),
            temperature=float(os.getenv("TEMPERATURE", "0.3")),
        )
        return response.choices[0].message.content or ""
    except Exception as error:
        fallback = os.getenv("EXTRACTIVE_FALLBACK", "true").lower() in ("1", "true", "yes")
        if not fallback:
            return f"Error while answering: {type(error).__name__}: {error}"
        return f"Groq unavailable ({type(error).__name__}: {error}).\n\n{_extractive_answer(retriever, query)}"


def _zero_gpu_on_huggingface(function):
    if os.getenv("SPACE_ID"):
        return spaces.GPU(function)
    return function


@_zero_gpu_on_huggingface
def classify_text(text: str) -> str:
    if not text or not text.strip():
        return "Please enter text to analyze."
    prediction = _get_sentiment_pipeline()(text, truncation=True, max_length=512)[0]
    return f"{prediction['label'].title()} sentiment ({prediction['score']:.1%} confidence)"


with gr.Blocks(title="Fasten Your Seat Belts — App Portal") as demo:
    gr.Markdown("# Fasten Your Seat Belts\nSQL and RAG run on CPU. The sentiment app uses a pretrained DistilBERT model and downloads its weights on first use.")

    with gr.Tab("Enterprise SQL Assistant"):
        gr.Markdown("Ask about the sample company database. Only predefined read-only SQL queries run; the data stays in memory.")
        sql_question = gr.Textbox(label="Question", placeholder="e.g. What is the total sales?")
        gr.Examples(
            examples=["Show all customers", "What is the total sales?", "Sales by customer name", "Orders placed in October 2026", "Customers from Egypt"],
            inputs=sql_question,
        )
        sql_submit = gr.Button("Ask", variant="primary")
        generated_sql = gr.Code(label="Generated read-only SQL", language="sql")
        sql_result = gr.Markdown(label="Result")
        sql_submit.click(answer_sql, inputs=sql_question, outputs=[generated_sql, sql_result])
        sql_question.submit(answer_sql, inputs=sql_question, outputs=[generated_sql, sql_result])

    with gr.Tab("RAG PDF Q&A"):
        gr.Markdown("Upload a PDF and ask questions grounded in it. Set GROQ_API_KEY in Space secrets for generated answers; without it, relevant passages are shown instead.")
        pdf_input = gr.File(label="PDF", file_types=[".pdf"], type="filepath")
        rag_question = gr.Textbox(label="Question", lines=2)
        rag_submit = gr.Button("Ask", variant="primary")
        rag_answer = gr.Markdown("*Answer will appear here.*")
        rag_submit.click(answer_rag, inputs=[pdf_input, rag_question], outputs=rag_answer)
        rag_question.submit(answer_rag, inputs=[pdf_input, rag_question], outputs=rag_answer)

    with gr.Tab("Real Sentiment Model"):
        gr.Markdown(f"English positive/negative sentiment using {SENTIMENT_MODEL}. First prediction downloads the model.")
        classifier_text = gr.Textbox(label="Text", lines=2, placeholder="This product is excellent and easy to use.")
        classifier_submit = gr.Button("Analyze sentiment", variant="primary")
        classifier_result = gr.Textbox(label="Prediction", interactive=False)
        classifier_submit.click(classify_text, inputs=classifier_text, outputs=classifier_result)
        classifier_text.submit(classify_text, inputs=classifier_text, outputs=classifier_result)

if __name__ == "__main__":
    demo.queue(default_concurrency_limit=1)
    demo.launch(server_name="0.0.0.0", server_port=int(os.getenv("PORT", "7860")))
