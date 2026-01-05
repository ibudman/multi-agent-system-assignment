from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.mongo import connect_mongo, disconnect_mongo, get_db_name, init_db
from openai import OpenAI
from tavily import TavilyClient
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    mongo_client = connect_mongo()
    app.state.mongo_client = mongo_client
    db_name = get_db_name()
    init_db(mongo_client[db_name])
    app.state.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    app.state.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    # TODO: add other clients here

    try:
        yield
    finally:
        # Shutdown
        # TODO: add other clients here
        disconnect_mongo(mongo_client)
