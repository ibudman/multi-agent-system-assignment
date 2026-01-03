from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.mongo import connect_mongo, disconnect_mongo


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongo_client = connect_mongo()
    app.state.mongo_client = mongo_client
    # TODO: add other clients here

    try:
        yield
    finally:
        # Shutdown
        # TODO: add other clients here
        disconnect_mongo(mongo_client)
