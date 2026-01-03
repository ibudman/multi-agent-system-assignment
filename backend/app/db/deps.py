from fastapi import Request
from pymongo.database import Database
from pymongo.collection import Collection
from app.db.mongo import (
    get_db_name,
    REQUESTS_COLLECTION,
    AGENT_RUNS_COLLECTION,
    RESULTS_COLLECTION,
)


def get_db(request: Request) -> Database:
    client = request.app.state.mongo_client
    return client[get_db_name()]


def get_requests_collection(request: Request) -> Collection:
    return get_db(request)[REQUESTS_COLLECTION]


def get_agent_runs_collection(request: Request) -> Collection:
    return get_db(request)[AGENT_RUNS_COLLECTION]


def get_results_collection(request: Request) -> Collection:
    return get_db(request)[RESULTS_COLLECTION]
