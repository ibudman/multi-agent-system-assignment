from fastapi import FastAPI
from dotenv import load_dotenv
from pathlib import Path
from app.api.routes import router
from app.core.lifespan import lifespan

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=False)

app = FastAPI(title="Multi-Agent System Assignment", lifespan=lifespan)

app.include_router(router)
