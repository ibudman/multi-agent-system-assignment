from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/health")
def health_check():
    return {"status": "ok"} # TODO: implement


@router.post("/learning-paths")
# TODO: define payload Pydantic model
def generate_learning_paths(payload: dict):
    return {
        "received": payload # TODO: implement
    }
