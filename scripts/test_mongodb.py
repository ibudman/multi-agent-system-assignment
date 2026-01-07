import os
from pathlib import Path
from dotenv import load_dotenv
from pymongo import MongoClient
import certifi

env_path = Path(__file__).resolve().parent.parent / "backend" / ".env"
load_dotenv(dotenv_path=env_path)

uri = os.getenv("MONGODB_URI")
if not uri:
    raise RuntimeError("MONGODB_URI not set")

client = MongoClient(
    uri,
    serverSelectionTimeoutMS=5000,
    tlsCAFile=certifi.where(),
)

client.admin.command("ping")
print("MongoDB connection works ✅")
