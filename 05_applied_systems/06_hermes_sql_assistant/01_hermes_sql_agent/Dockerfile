# SQL Assistant — FastAPI + Docker

FROM python:3.12-slim

WORKDIR /app

# Copy dependency manifest first (layers cache)
COPY 01_hermes_sql_agent/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the whole repo (includes database/ + app/)
COPY 01_hermes_sql_agent /app/01_hermes_sql_agent

EXPOSE 8000

# Run the FastAPI service
CMD ["uvicorn", "01_hermes_sql_agent.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
