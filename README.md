# Healthy Meal Agent

Healthy Meal Agent is an AI agent project for recommending meals based on user conditions and validating them against nutrition guidelines.

This repository is currently in the initialization stage. It includes a minimum FastAPI backend, Streamlit frontend, and deterministic mock agent pipeline for early testing.

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
|-- app/
|   |-- schemas.py
|   |-- data/
|   |   `-- foods_clean.csv
|   |-- services/
|   |   |-- food_retriever.py
|   |   |-- meal_composer.py
|   |   |-- nutrition_calculator.py
|   |   `-- validator.py
|   `-- agents/
|       `-- mock_agent.py
|-- tests/
|   |-- test_health.py
|   |-- test_mock_agent.py
|   |-- test_retriever.py
|   `-- test_validator.py
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- .gitignore
|-- pyproject.toml
|-- requirements.txt
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

Alternatively:

```bash
pip install -r requirements.txt
pip install -e .
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

## Mock Agent

The mock agent uses local CSV data and deterministic Python functions only. It does not call an LLM, RAG system, or database yet.

```python
from app.agents.mock_agent import run_mock_agent
from app.schemas import MealRequest

result = run_mock_agent(MealRequest(target_kcal=500))
print(result.meal_plan)
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
- Local CSV-backed mock agent scaffold
- Basic CI workflow for lint and tests

No production meal recommendation, RAG, database, or LLM logic is implemented yet.
