# Learning Path Explorer

A multi-agent system that discovers, extracts, and structures learning programs into short-, medium-, and long-term
learning paths based on a user query and preferences.

## Key Features

With this application, you can:

- Generate learning options from a free-text query, with optional preferences (format, goal, budget, location)
- Organize results into short-, medium-, and long-term learning horizons
- View key program details side-by-side to compare different options
- Access source links and citations for all web-sourced information
- Export each learning horizon independently as JSON or CSV

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

Create `.env` files based on the provided `.env.example` files in both the `backend/` and `frontend/` directories.

### Backend

| Variable              | Description                                          |
|-----------------------|------------------------------------------------------|
| OPENAI_API_KEY        | OpenAI API key used for schema-based extraction      |
| TAVILY_API_KEY        | Tavily API key for web search and content extraction |
| MONGODB_URI           | MongoDB Atlas connection string                      |
| MONGODB_DB            | MongoDB database name                                |
| CORS_ORIGINS          | Allowed frontend origin for CORS                     |
| AWS_ACCESS_KEY_ID     | AWS access key                                       |
| AWS_SECRET_ACCESS_KEY | AWS secret access key                                |
| AWS_DEFAULT_REGION    | AWS region                                           |

#### Mock & Testing Controls

| Variable      | Description                                                 |
|---------------|-------------------------------------------------------------|
| MOCK_EXTERNAL | Toggle external integrations (`1` = mocks, `0` = real APIs) |
| MOCK_MODE     | Mock scenario selector (`ux` or `photography`)              |

When `MOCK_EXTERNAL=1`, the system returns deterministic mock outputs for testing and development.

These variables are optional; by default, `MOCK_EXTERNAL` is set to `0` and the system uses real external API calls.

### Frontend

| Variable          | Description                 |
|-------------------|-----------------------------|
| VITE_API_BASE_URL | Base URL of the backend API |

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

## Running the Frontend

From the `frontend/` directory:

```bash
npm run dev
```

The frontend will be available at [http://localhost:5173](http://localhost:5173).

## Running Tests

From the `backend/` directory:

```bash
pytest
```

Tests focus on service-level logic and graph orchestration.
All external integrations are mocked at the test level to ensure fully deterministic and isolated test runs.

## API Endpoints

- `POST /learning-paths` – Generate a personalized learning path
- `GET /health` – Health check endpoint
