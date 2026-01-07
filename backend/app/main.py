import os
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app = FastAPI(title="Multi-Agent System Assignment", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
