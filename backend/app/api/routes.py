from fastapi import APIRouter, Request, HTTPException
from app.db.deps import (
    get_requests_collection,
    get_agent_runs_collection,
    get_results_collection,
)
from app.db.repos import RequestsRepo, AgentRunsRepo, ResultsRepo
from app.graph.runner import GraphRunner
from app.models.schemas import (
    HealthCheckResponse,
    LearningPathsRequest,
    LearningPathsResponse,
)
from app.services.learning_paths import LearningPathsService

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check() -> HealthCheckResponse:
    empty_response = HealthCheckResponse(status="ok")
    return empty_response


@router.post("/learning-paths")
def generate_learning_paths(
    request: Request, payload: LearningPathsRequest
) -> LearningPathsResponse:
    requests_repo = RequestsRepo(get_requests_collection(request))
    agent_runs_repo = AgentRunsRepo(get_agent_runs_collection(request))
    results_repo = ResultsRepo(get_results_collection(request))

    runner = GraphRunner(agent_runs_repo=agent_runs_repo)
    service = LearningPathsService(
        requests_repo=requests_repo,
        agent_runs_repo=agent_runs_repo,
        results_repo=results_repo,
        runner=runner,
    )
    try:
        return service.generate(payload)
    except Exception:
        raise HTTPException(status_code=500, detail="Processing failed")
