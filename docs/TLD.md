# Technical Design (TLD) – Learning Path Explorer

## 1. Introduction and Overview

Learning Path Explorer is a web-based system that processes a user’s learning query through a coordinated set of agents to discover, extract, and organize learning programs from the web. This document describes the technical design of the system, focusing on architecture, component responsibilities, data flow, interfaces, and deployment.

The system is implemented as a backend service that orchestrates multiple agents using LangGraph. Tavily APIs are used for web discovery and structured data extraction, OpenAI models are used for interpretation and synthesis, and MongoDB Atlas is used to persist requests, agent outputs, and final results.

The backend executes the learning-path pipeline synchronously. Each request is processed end-to-end within a single request–response cycle and is associated with a unique request identifier for persistence and logging.

## 2. System Architecture

### High-level architecture diagram

```text
+------------------+
|     Web UI       |
+------------------+
        |
        |  HTTP
        v
+--------------------------------------------------+
|                   Backend API                    |
|                                                  |
|   +------------------------------------------+   |
|   |               LangGraph                  |   |
|   |                                          |   |
|   |   +-----------+                          |   |
|   |   |  Agent 1  |                          |   |
|   |   +-----------+                          |   |
|   |          |                               |   |
|   |          v                               |   |
|   |   +-----------+                          |   |
|   |   |  Agent 2  |                          |   |
|   |   +-----------+                          |   |
|   |          |                               |   |
|   |          v                               |   |
|   |   +-----------+                          |   |
|   |   |  Agent 3  |                          |   |
|   |   +-----------+                          |   |
|   |                                          |   |
|   +------------------------------------------+   |
|       |                              |           |
+-------|------------------------------|-----------+
        |               |              |
        |               |              |
        v               |              v
+------------------+    |     +------------------+
|     OpenAI       |    |     |      Tavily      |
+------------------+    |     +------------------+
                        |
                        |
                        |
                        v
                +------------------+
                |    MongoDB       |
                +------------------+


```

### Request Flow

1. The Web UI sends a `POST` request to the Backend API containing the learning query and optional preferences.
2. The Backend API generates a unique `request_id` and stores the initial request in MongoDB.
3. The Backend executes the LangGraph pipeline, where agents invoke external services such as Tavily and OpenAI.
4. Intermediate agent outputs and the final structured result are persisted in MongoDB.
5. The Backend API returns the grouped learning paths to the Web UI in the same request–response cycle.

## 3. Backend APIs

### Backend APIs

| Endpoint | Method | Input (Body / Params) | Output (JSON) | Description |
|--------|--------|------------------------|---------------|-------------|
| `/api/learning-paths` | POST | **Body:**<br>• `query` (string, required)<br>• `prefs` (JSON object, optional) | • `request_id`<br>• `results`<br>• `warnings` | Triggers the learning-path discovery pipeline and returns grouped learning options. |
| `/api/health` | GET | None | • `status` | Health check endpoint used by AWS deployment and monitoring to verify service availability. |

**`prefs` JSON structure**
```json
{
  "format": "online | in-person | hybrid | null",
  "goal": "hobby | career | skill improvement | null",
  "budget": "free | low-cost | paid | null",
  "city": "string | null"
}
```

**`results` JSON structure**
```json
{
  "short_term": Program[],
  "medium_term": Program[],
  "long_term": Program[]
}
```

**`Program` JSON structure**
```json
{
  "program_name": "string",
  "provider": "string",
  "topics_covered": ["string"],
  "format": "online | in-person | hybrid | Not specified",
  "duration": "string",
  "cost": "string",
  "prerequisites": "string",
  "location": "string",
  "who_this_is_for": "string",
  "source_link": "string (URL)",
  "citation": "string (URL)"
}
```

## 4. Component Design (LangGraph + Agents)


### Overview

The system follows a Sequential StateGraph pattern. Each node represents a specialized agent that performs a discrete task and updates a shared state object before control transitions to the next node.

### Shared State Object

| Field | Type | Description |
|------|------|-------------|
| `request_id` | string | Unique identifier for the request |
| `input` | object | User query and optional preferences |
| `raw_leads` | array | List of discovered learning leads |
| `extracted_programs` | array | List of structured Program objects |
| `results` | object | Final categorized learning paths |
| `warnings` | array | Non-blocking issues encountered during processing |

**`input` structure**
```json
{
  "query": "string",
  "prefs": {
    "format": "online | in-person | hybrid | null",
    "goal": "hobby | career | skill improvement | null",
    "budget": "free | low-cost | paid | null",
    "city": "string | null"
  }
}
```

**`raw_leads` structure**
```json
[
  {
    "url": "string (URL)",
    "title": "string | null",
    "snippet": "string | null",
    "source": "string | null"
  }
]
```

**`extracted_programs` structure**
```json
Program[]
```

**`results` structure**
```json
{
  "short_term": Program[],
  "medium_term": Program[],
  "long_term": Program[]
}
```

**`warnings` structure**
```json
[
  "string"
]
```

### Agent Definitions

The LangGraph workflow is implemented as a sequential StateGraph:
`Adaptive Scout → Extraction Specialist → Path Organizer`

Each agent performs a discrete task and updates the shared state.

#### Agent 1: Adaptive Scout (Discovery)

**Responsibility**  
Find relevant learning programs on the web based on the user’s query and preferences.

**Tools**  
- Tavily: `search`

**Reads from state**  
- `input.query`  
- `input.prefs`

**Writes to state**  
- `raw_leads` (list of leads)
- `warnings` (may append)

**Core logic**  
- Build 2–3 search queries from the user query and preferences.  
- Treat preferences as priorities, not strict filters.  
- Collect URLs with lightweight context (title, snippet, source).  
- Remove duplicate URLs and optionally dedupe by domain.

**Constraints**  
- Max leads 
- Results per query
- Max search queries

**Failure behavior**  
- If no leads are found, return an empty list and add a warning.


#### Agent 2: Extraction Specialist (Structured Program Builder)

**Responsibility**  
Transform discovered program pages into structured `Program` objects that match the defined 11-column output schema.

**Tools**  
- Tavily: `extract`  
- OpenAI (LLM): structured output for schema mapping and normalization  
- Pydantic: schema validation of extracted `Program` objects

**Reads from state**  
- `raw_leads` (list of leads)

**Writes to state**  
- `extracted_programs` (list of `Program` objects)
- `warnings` (may append)

**Core logic**  
- Select up to N leads from `raw_leads` for extraction.  
- For each selected lead:  
  - Call Tavily `extract` to retrieve the page’s relevant content.  
  - Truncate or summarize extracted content to fit within a configured token budget.  
  - Pass the extracted content to the OpenAI model with a strict schema prompt to produce a `Program` object.  
- Use the LLM to:  
  - Populate `topics_covered` as a short list of topics.  
  - Generate a concise `who_this_is_for` summary.  
  - Normalize format variants (e.g., “remote”, “virtual”, “zoom”) into `online`, `in-person`, or `hybrid`.  
- Enforce “no guessing”:  
  - If cost, duration, or prerequisites are not explicitly present, return `"Not specified"`.  
- Validate each `Program` object using Pydantic before adding it to `extracted_programs`.  
- Always set `source_link` and `citation` to the extracted URL.

**Constraints**  
- Max URLs to extract
- Token limit per page for LLM input

**Failure behavior**  
- If extraction or validation fails for a URL, skip it and add a warning.  
- If all extractions fail, return an empty list and add a warning.

#### Agent 3: Path Organizer (Bucketing + Final Assembly)

**Responsibility**  
Group `extracted_programs` into short-, medium-, and long-term learning paths and assemble the final `results` object for the UI.

**Tools**  
- None

**Reads from state**  
- `extracted_programs`

**Writes to state**  
- `results`  
- `warnings` (may append)

**Core logic**  
- Bucket programs into:
  - `short_term`
  - `medium_term`
  - `long_term`
- Use `duration` when clearly specified.
- If `duration` is `"Not specified"`:
  - Check provider and title keywords:
    - If provider/title indicates **Degree / University / Bachelor / Master** → bucket as `long_term`
    - If provider/title indicates **Workshop / Intro / Crash course** → bucket as `short_term`
    - Otherwise default to `medium_term`
  - Append a warning that bucketing used fallback heuristics due to missing duration.
- Enforce:
  - No duplicate programs across buckets
  - Max programs per bucket
- If one or more buckets end up empty, append a warning.
- If total number of programs is low, append a warning.

**Constraints**  
- Max programs per bucket

**Failure behavior**  
- If `extracted_programs` is empty:
  - Return empty buckets
  - Append a warning indicating that no programs were available to organize


### Graph Flow & Error Handling

#### Graph Flow Overview
The system uses a linear flow with embedded resilience. Instead of complex conditional branching, it prioritizes completing the request with partial success over failing entirely.

#### Graph Transitions
- **START → Adaptive Scout**  
  Triggered on user POST request.

- **Adaptive Scout → Extraction Specialist**  
  Proceeds if `raw_leads` contains at least one URL.

- **Extraction Specialist → Path Organizer**  
  Proceeds with all successfully validated `Program` objects.

- **Path Organizer → END**  
  Finalizes the `results` object for the API response.

#### Error Strategy

- **Node-Level Retries**  
  Nodes that rely on external APIs use a basic retry policy to handle transient Tavily or OpenAI timeouts.

- **Warning Buffer**  
  Each node is wrapped in error handling logic. If a non-critical error occurs (e.g., a single URL fails extraction), the issue is appended to the `warnings` list in the shared state and the graph continues.

- **Hard Stop**  
  If the Adaptive Scout finds zero leads, the graph terminates early before running the Extraction Specialist, returning empty results with a “No leads found” warning.

- **State Recovery**  
  Since MongoDB is updated after each agent run, the `request_id` allows developers to inspect which agent completed successfully if the pipeline does not reach the END node.


## 5. Data Model

The system uses MongoDB Atlas as a document-oriented data store to persist request lifecycle data.
Data is organized into collections, each containing documents linked by a shared `request_id`.

---


### Collection: `requests`

| Field | Type | Description |
|------|------|-------------|
| `_id` | ObjectId | MongoDB-generated primary key |
| `request_id` | string | Application-level unique identifier used to link documents across collections (indexed, unique) |
| `created_at` | timestamp | Time when the request was received |
| `status` | string | Request execution status: `running`, `completed`, or `failed` |
| `input` | JSON object | Original user input (see structure below) |
| `error` | string \| null | Request-level error message if failed, otherwise `null` |

**`input` JSON structure**
```json
{
  "query": "string",
  "format": "online | in-person | hybrid | null",
  "goal": "hobby | career | skill improvement | null",
  "budget": "free | low-cost | paid | null",
  "city": "string | null"
}
```

### Collection: `agent_runs`

| Field | Type | Description |
|------|------|-------------|
| `_id` | ObjectId | MongoDB-generated primary key |
| `request_id` | string | Links this agent run to the parent request (indexed, non-unique) |
| `agent_name` | string | Name of the executed agent |
| `started_at` | timestamp | Agent execution start time |
| `ended_at` | timestamp | Agent execution end time |
| `output_summary` | JSON object | Lightweight summary of agent output |
| `warnings` | array | Non-fatal issues encountered during agent execution |
| `error` | string \| null | Agent-level error message if failed, otherwise `null` |

**`output_summary` example**
```json
{
  "counts": {
    "raw_leads": 12,
    "extracted_programs": 8
  },
  "selected_urls": [
    "https://example.com/course-1",
    "https://example.com/course-2"
  ]
}
```

### Collection: `results`

This collection stores the final structured output returned to the user after the full pipeline completes.

| Field | Type | Description |
|------|------|-------------|
| `_id` | ObjectId | MongoDB-generated primary key |
| `request_id` | string | Links this result to the parent request (indexed, unique) |
| `created_at` | timestamp | Time when the final result was produced |
| `paths` | JSON object | Grouped learning paths (see structure below) |
| `warnings` | array | Non-fatal issues encountered across the full request |
| `error` | string \| null | Result-level error message if generation failed, otherwise `null` |

**`paths` JSON structure**
```json
{
  "short_term": [Program],
  "medium_term": [Program],
  "long_term": [Program]
}
```

**`Program` JSON structure**
```json
{
  "program_name": "string",
  "provider": "string",
  "topics_covered": ["string"],
  "format": "string",
  "duration": "string",
  "cost_usd": "number | null",
  "cost_text": "string",
  "prerequisites": "string",
  "location": "string",
  "who_this_is_for": "string",
  "source_link": "string (URL)",
  "citation": "string (URL)"
}
```





