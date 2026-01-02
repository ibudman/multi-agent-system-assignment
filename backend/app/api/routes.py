from fastapi import APIRouter
import uuid
from app.models.schemas import (
    HealthCheckResponse,
    LearningPathsRequest,
    LearningPathsResponse,
    LearningPathsResults,
)

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check() -> HealthCheckResponse:
    empty_response = HealthCheckResponse(status="ok") # TODO: implement logic
    return empty_response


@router.post("/learning-paths")
def generate_learning_paths(payload: LearningPathsRequest) -> LearningPathsResponse:
    # TODO: implement logic
    request_id = uuid.uuid4()

    empty_results = LearningPathsResults(
        short_term=[],
        medium_term=[],
        long_term=[],
    )

    return LearningPathsResponse(
        request_id=request_id,
        results=empty_results,
        warnings=["placeholder: pipeline not implemented"],
    )
