from fastapi import FastAPI
from dotenv import load_dotenv, find_dotenv
from app.api.routes import router
from app.core.lifespan import lifespan

load_dotenv(find_dotenv(), override=False)

app = FastAPI(title="Multi-Agent System Assignment", lifespan=lifespan)

app.include_router(router)
