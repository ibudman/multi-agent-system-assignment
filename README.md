# Learning Path Explorer

A multi-agent system that generates personalized learning paths based on user goals, preferences, and constraints, using
LangGraph and external knowledge sources.

## Documentation

- [Product Requirements Document (PRD)](docs/PRD.md)
- [Top Level Design (TLD)](docs/TLD.md)

## Project Structure (High-Level)

- `backend/` – FastAPI backend, LangGraph agents, persistence, and integrations
- `frontend/` – Simple web UI for submitting queries and viewing results
- `docs/` – Product and technical documentation

## Architecture & Agents

The system is implemented as a multi-agent workflow using LangGraph, where a graph orchestrates execution and agents
perform domain-specific tasks such as search, extraction, and validation.

Detailed architecture, agent responsibilities, and data flow are documented in the [TLD](docs/TLD.md).

## Environment Variables

| Variable              | Description                                          |
|-----------------------|------------------------------------------------------|
| OPENAI_API_KEY        | OpenAI API key used for schema-based extraction      |
| TAVILY_API_KEY        | Tavily API key for web search and content extraction |
| MONGODB_URI           | MongoDB Atlas connection string                      |
| MONGODB_DB            | MongoDB database name                                |
| FRONTEND_ORIGIN       | Allowed frontend origin for CORS                     |
| AWS_ACCESS_KEY_ID     | AWS access key                                       |
| AWS_SECRET_ACCESS_KEY | AWS secret access key                                |
| AWS_DEFAULT_REGION    | AWS region                                           |

### Mock & Testing Controls

| Variable      | Description                                                 |
|---------------|-------------------------------------------------------------|
| MOCK_EXTERNAL | Toggle external integrations (`1` = mocks, `0` = real APIs) |
| MOCK_MODE     | Mock scenario selector (`ux` or `photography`)              |

When `MOCK_EXTERNAL=1`, the system returns deterministic mock outputs for testing and development.

## Data Persistence & Observability

Each request is tracked end-to-end using a generated `request_id`, which links documents across
the `requests`, `agent_runs`, and `results` collections in MongoDB.

In addition, the backend emits minimal server logs at request start, completion, and on unexpected
failures to aid debugging without duplicating persisted execution data.

## Running the Backend

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

## Running Tests

From the `backend/` directory:

```bash
pytest
```

Tests focus on service-level logic and graph orchestration, with all external dependencies mocked.

## API Endpoints

- `POST /learning-paths` – Generate a personalized learning path
- `GET /health` – Health check endpoint
