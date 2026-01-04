from fastapi import APIRouter, Request, HTTPException
import uuid
from datetime import datetime, timezone
from app.db.deps import get_requests_collection
from app.models.schemas import (
    HealthCheckResponse,
    LearningPathsRequest,
    LearningPathsResponse,
    LearningPathsResults,
)
from app.db.models import RequestDoc, RequestInput

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check() -> HealthCheckResponse:
    empty_response = HealthCheckResponse(status="ok")
    return empty_response


@router.post("/learning-paths")
def generate_learning_paths(
    request: Request, payload: LearningPathsRequest
) -> LearningPathsResponse:
    request_id = uuid.uuid4()
    request_id_str = str(request_id)

    requests_col = get_requests_collection(request)
    doc = RequestDoc(
        request_id=request_id_str,
        created_at=datetime.now(timezone.utc),
        status="running",
        input=RequestInput(
            query=payload.query,
            prefs=(payload.prefs.model_dump() if payload.prefs else None),
        ),
        error=None,
    )
    requests_col.insert_one(doc.model_dump())

    try:
        # TODO: implement logic
        empty_results = LearningPathsResults(
            short_term=[],
            medium_term=[],
            long_term=[],
        )

        # update on success
        requests_col.update_one(
            {"request_id": request_id_str},
            {
                "$set": {
                    "status": "completed",
                }
            },
        )

        return LearningPathsResponse(
            request_id=request_id,
            results=empty_results,
            warnings=["placeholder: pipeline not implemented"],
        )

    except Exception as e:
        # mark failed in requests collection - status, error
        requests_col.update_one(
            {"request_id": request_id_str},
            {
                "$set": {
                    "status": "failed",
                    "error": str(e),
                }
            },
        )

        raise HTTPException(status_code=500, detail="Processing failed")
