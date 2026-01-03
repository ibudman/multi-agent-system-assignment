from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.mongo import connect_mongo, disconnect_mongo, get_db_name, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongo_client = connect_mongo()
    app.state.mongo_client = mongo_client
    db_name = get_db_name()
    init_db(mongo_client[db_name])
    # TODO: add other clients here

    try:
        yield
    finally:
        # Shutdown
        # TODO: add other clients here
        disconnect_mongo(mongo_client)
