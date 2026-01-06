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
| `extracted_programs` | array | List of structured ProgramRecord objects |
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
ProgramRecord[]
```

**`results` structure**
```json
{
  "short_term": ProgramRecord[],
  "medium_term": ProgramRecord[],
  "long_term": ProgramRecord[]
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
Transform discovered program pages into structured `ProgramRecord` objects that match the persisted output schema.

**Tools**  
- Tavily: `extract`  
- OpenAI (LLM): structured output for schema mapping and normalization  
- Pydantic: schema validation of extracted `ProgramRecord` objects

**Reads from state**  
- `raw_leads` (list of leads)

**Writes to state**  
- `extracted_programs` (list of `ProgramRecord` objects)
- `warnings` (may append)

**Core logic**  
- Select up to N leads from `raw_leads` for extraction.  
- For each selected lead:  
  - Call Tavily `extract` to retrieve the page’s relevant content.  
  - Truncate or summarize extracted content to fit within a configured token budget.  
  - Pass the extracted content to the OpenAI model with a strict schema prompt to produce a `ProgramRecord` object.  
- Use the LLM to:  
  - Populate `topics_covered` as a short list of topics.  
  - Generate a concise `who_this_is_for` summary.  
  - Normalize format variants (e.g., “remote”, “virtual”, “zoom”) into `online`, `in-person`, or `hybrid`.  
- Enforce “no guessing”:  
  - If duration or prerequisites are not explicitly present, return `"Not specified"`.
  - If format is unclear or not stated, return `"Not specified"`.
  - If cost is not explicitly present, set cost_text to `"Not specified"` and cost_usd to `null`.
  - If cost is present, set cost_text from the page; set cost_usd only when a numeric USD amount is explicitly stated (otherwise `null`).
- Validate each `ProgramRecord` object using Pydantic before adding it to `extracted_programs`.  
- Always set `source_link` and `citation` to the extracted URL.

**Constraints**  
- Max URLs to extract
- Token limit per page for LLM input

**Failure behavior**  
- If extraction or validation fails for a URL, skip it and add a warning.  
- If all extractions fail, return an empty list and add a warning.

#### Agent 3: Path Organizer (Bucketing + Final Assembly)

**Responsibility**  
Group `extracted_programs` into short-, medium-, and long-term learning paths and assemble the final categorized `results`, later mapped to API response.

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
  Proceeds with all successfully validated `ProgramRecord` objects.

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
  "prefs": {
    "format": "online | in-person | hybrid | null",
    "goal": "hobby | career | skill improvement | null",
    "budget": "free | low-cost | paid | null",
    "city": "string | null"
  }
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


`output_summary` is cumulative and reflects the pipeline state after the current agent finishes.
Individual fields are populated by different agents as they run, and may be absent if the responsible agent has not executed yet.

**example**
```json
{
  "counts": {
    "raw_leads": 12, // agent 1
    "extracted_programs": 8 // agent 2
  },
  "selected_urls": [
    "https://example.com/course-1",
    "https://example.com/course-2"
  ], // agent 1
  "bucket_counts": {
    "short_term": 3,
    "medium_term": 4,
    "long_term": 1
  }// agent 3
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
  "short_term": [ProgramRecord],
  "medium_term": [ProgramRecord],
  "long_term": [ProgramRecord]
}
```

**`ProgramRecord` JSON structure**
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

## 6. User Interface Design

The system includes a simple, single-page web interface used to submit learning queries and view results.

The UI allows users to:
- Enter a free-text learning goal
- Optionally select preferences (format, goal, budget, city)
- Trigger the backend pipeline via a single action
- View the returned learning paths as structured tables
- Export results in JSON or CSV format

The UI is stateless and driven entirely by the backend response.  
It does not perform client-side inference, filtering, or data transformation.


## 7. Error Handling & Observability

The system is designed to favor partial success over complete failure whenever possible.

Errors are handled at two levels:
- **Blocking errors**, which prevent the request from completing (e.g., repeated external API failures, database write failures)
- **Non-blocking errors**, which affect only part of the pipeline (e.g., a single URL failing extraction)

Non-blocking errors do not stop execution. Instead, the system continues processing remaining items and records diagnostic information internally.

Each request is associated with a unique `request_id`, which is persisted in MongoDB along with intermediate agent outputs. This allows developers to trace how far a request progressed and identify which agent encountered issues.

Basic observability is provided through structured logging at each agent step. Logs include the `request_id`, agent name, and high-level status (started, completed, failed).

Warnings and partial failures are stored internally for debugging purposes and are not exposed directly to the end user.

## 8. Security & Configuration

The system is configured using environment variables to manage all external dependencies.

API keys and connection strings for OpenAI, Tavily, and MongoDB Atlas are provided via environment variables and are not stored in source control.

## 9. Deployment Plan

The backend service is deployed on AWS using Elastic Beanstalk to keep deployment simple and production-oriented.

Elastic Beanstalk supports running multiple instances via an Auto Scaling group, allowing the backend to scale horizontally if needed.

MongoDB Atlas is used as the managed database service. The backend connects to the Atlas cluster using the official MongoDB Python client and a connection string provided via environment variables.

The frontend is a simple web UI that allows users to submit queries, trigger the pipeline, view results, and export outputs. The frontend can be deployed as a static site (e.g., S3 or similar static hosting) and is configured to call the deployed backend API.

High-level deployment and validation steps:
- Deploy the backend to Elastic Beanstalk
- Configure environment variables in the Elastic Beanstalk environment (OpenAI, Tavily, MongoDB)
- Verify connectivity to MongoDB Atlas from the deployed backend
- Deploy the frontend and confirm Frontend ↔ Backend ↔ MongoDB integration
- Validate correctness by issuing test queries and confirming request data, agent outputs, and final results are logged in MongoDB
