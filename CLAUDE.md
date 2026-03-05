# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Learning Path Explorer is a multi-agent system that discovers, extracts, and structures learning programs into short-, medium-, and long-term learning paths based on a user query and preferences. It consists of a FastAPI backend (Python) and a React/TypeScript frontend.

## Commands

### Backend (from `backend/` directory)

```bash
# Run development server
uvicorn app.main:app --reload

# Run all tests
pytest

# Run a single test file
pytest tests/unit/test_learning_paths_service.py

# Run a single test by name
pytest tests/unit/test_graph_runner.py::test_name
```

### Frontend (from `frontend/` directory)

```bash
npm run dev        # Start dev server (http://localhost:5173)
npm run build      # TypeScript compile + Vite build
npm run lint       # ESLint
npm run preview    # Preview production build
```

## Environment Setup

### Backend `.env` (in `backend/`)

```
OPENAI_API_KEY=...
TAVILY_API_KEY=...
MONGODB_URI=...
MONGODB_DB=...
CORS_ORIGINS=http://localhost:5173

# Optional: use mocks instead of real APIs
MOCK_EXTERNAL=1         # 1 = mocks, 0 = real (default: 0)
MOCK_MODE=ux            # "ux" or "photography"
```

### Frontend `.env` (in `frontend/`)

```
VITE_API_BASE_URL=http://localhost:8000
```

## Architecture

### LangGraph Pipeline (backend/app/graph/)

The core of the backend is a synchronous LangGraph pipeline executed per request:

```
START -> scout -> (conditional) -> extract -> organize -> END
```

1. **`adaptive_scout`** (`nodes/adaptive_scout.py`): Takes user query + prefs, generates 2-3 search queries, calls Tavily search, returns `raw_leads` (up to 12 URLs with metadata).
2. **`extraction_specialist`** (`nodes/extraction_specialist.py`): Fetches content for each lead via Tavily extract, uses OpenAI to parse structured `ProgramRecord` objects. Returns `extracted_programs`.
3. **`path_organizer`** (`nodes/path_organizer.py`): Uses OpenAI to classify programs into short/medium/long-term horizons. Returns `results`.

If `scout` returns no leads, the graph short-circuits to `END` (conditional edge).

`GraphState` uses `operator.add` reducers for `raw_leads`, `extracted_programs`, and `warnings` (nodes append to these lists). `results` is fully overwritten by `organize`.

### Request Lifecycle & Persistence

Each request gets a `request_id` (UUID). Three MongoDB collections track state:
- `requests`: status tracking (`running` -> `completed`/`failed`), input, timestamps
- `agent_runs`: per-node execution records written by `GraphRunner`
- `results`: final structured paths (short/medium/long-term programs) + warnings

`LearningPathsService` (`services/learning_paths.py`) orchestrates the full lifecycle: persist request -> run graph -> persist results -> return response.

### External Clients

External clients (`OpenAI`, `TavilyClient`) are initialized once at startup via `lifespan` (`core/lifespan.py`) and stored on `app.state`. They're passed into `GraphDeps` and injected into nodes via `functools.partial`.

When `MOCK_EXTERNAL=1`, `external/mocks.py` provides fake implementations conforming to the protocols in `external/protocols.py`.

### Backend Module Layout

```
backend/app/
  main.py          # FastAPI app setup, CORS, router registration
  core/
    lifespan.py    # Startup/shutdown: connect MongoDB, init clients
    env.py         # Environment validation
  api/
    routes.py      # POST /api/learning-paths, GET /api/health
  services/
    learning_paths.py  # LearningPathsService: orchestrates request lifecycle
  graph/
    build.py       # Builds LangGraph StateGraph
    state.py       # GraphState TypedDict + InputPayload, RawLead definitions
    runner.py      # GraphRunner: runs compiled graph, records agent_runs
    deps.py        # GraphDeps dataclass (openai_client, tavily_client)
    protocols.py   # GraphRunnerProtocol for testing
    nodes/         # adaptive_scout, extraction_specialist, path_organizer
  db/
    mongo.py       # MongoDB connect/disconnect/init
    models.py      # RequestDoc, AgentRunDoc, ResultsDoc Pydantic models
    repos.py       # RequestsRepo, AgentRunsRepo, ResultsRepo
    protocols.py   # Repo protocols for testing/mocking
  models/
    base.py        # ProgramRecordBase (shared model)
    schemas.py     # API request/response schemas
  external/
    protocols.py   # TavilyClientProtocol, OpenAIClientProtocol
    mocks.py       # Mock implementations for local dev/testing
```

### Frontend

React + TypeScript (Vite). Single-page UI at `frontend/src/`:
- `App.tsx`: root component with form and results rendering
- `api/`: fetch calls to backend `/api/learning-paths`
- `components/`: UI components for displaying learning path results
- `types.ts`: TypeScript types mirroring API response schemas

## Testing

Tests live in `backend/tests/unit/`. All external integrations (OpenAI, Tavily, MongoDB) are mocked at the test level using the protocol interfaces (`db/protocols.py`, `external/protocols.py`, `graph/protocols.py`). The test suite focuses on service logic and graph orchestration.
