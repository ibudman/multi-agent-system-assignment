import os
from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)

raw = os.getenv("CORS_ORIGINS", "http://localhost:5173")
cors_origins = [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
app = FastAPI(title="Multi-Agent System Assignment", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
