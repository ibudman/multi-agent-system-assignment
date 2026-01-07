from contextlib import asynccontextmanager
from fastapi import FastAPI
from openai import OpenAI
from tavily import TavilyClient
import os
from app.external.mocks import make_mock_tavily_client, make_mock_openai_client
from app.core.env import validate_env
from app.db.mongo import connect_mongo, disconnect_mongo, get_db_name, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_env()
    # Startup
    mongo_client = connect_mongo()
    app.state.mongo_client = mongo_client
    db_name = get_db_name()
    init_db(mongo_client[db_name])

    mock_external = os.getenv("MOCK_EXTERNAL", "0") == "1"
    if mock_external:
        app.state.openai_client = make_mock_openai_client()
        app.state.tavily_client = make_mock_tavily_client()
    else:
        app.state.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        app.state.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

    try:
        yield
    finally:
        # Shutdown
        disconnect_mongo(mongo_client)
