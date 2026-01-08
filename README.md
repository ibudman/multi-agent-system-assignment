# multi-agent-system-assignment

A multi-agent system that uses LangGraph and the Tavily API to solve a real-world information task.

# Learning Path Explorer

## Documentation

- [Product Requirements Document (PRD)](docs/PRD.md)
- [Top Level Design (TLD)](docs/TLD.md)
-

### Environment Variables

| Variable              | Description                                  |
|-----------------------|----------------------------------------------|
| OPENAI_API_KEY        | OpenAI API key used for schema mapping       |
| TAVILY_API_KEY        | Tavily API key for web search and extraction |
| MONGODB_URI           | MongoDB Atlas connection string              |
| AWS_ACCESS_KEY_ID     | AWS access key for backend deployment        |
| AWS_SECRET_ACCESS_KEY | AWS secret access key for backend deployment |
| AWS_DEFAULT_REGION    | AWS region for backend deployment            |

### Data Persistence & Observability

Each request is tracked end-to-end using a generated `request_id`, which links documents across
the `requests`, `agent_runs`, and `results` collections in MongoDB.

In addition, the backend emits minimal server logs at request start, completion, and on unexpected
failures to aid debugging without duplicating persisted execution data.
