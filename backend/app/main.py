from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Multi-Agent System Assignment")

app.include_router(router)