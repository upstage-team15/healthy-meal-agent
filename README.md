# Healthy Meal Agent

Healthy Meal Agent is an AI agent project for recommending meals based on user conditions and validating them against nutrition guidelines.

This repository is currently in the initialization stage. It includes only the minimum FastAPI backend and Streamlit frontend scaffold needed to verify that the project can run.

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- Workflow: LangGraph planned
- LLM Gateway: LiteLLM planned
- Database: Supabase Postgres planned
- Vector Search: Supabase pgvector planned
- CI: GitHub Actions
- Deploy: Docker-based deployment planned

## Project Structure

```text
.
|-- backend/
|   `-- main.py
|-- frontend/
|   `-- app.py
|-- tests/
|   `-- test_health.py
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- .gitignore
|-- pyproject.toml
|-- uv.lock
`-- README.md
```

## Getting Started

### 1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e ".[dev]"
```

## Run Locally

### FastAPI

```bash
uvicorn backend.main:app --reload
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

### Streamlit

```bash
streamlit run frontend/app.py
```

## Quality Checks

```bash
ruff check .
pytest
```

## Current Scope

- Repository initialization
- Minimal FastAPI app startup check
- Minimal Streamlit app startup check
- Basic CI workflow for lint and tests

No meal recommendation, RAG, database, or LLM logic is implemented yet.
