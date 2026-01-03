import os
import certifi
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError


def connect_mongo() -> MongoClient:
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI not set")

    client = MongoClient(
        uri,
        serverSelectionTimeoutMS=5000,
        tlsCAFile=certifi.where(),
    )

    try:
        client.admin.command("ping")
    except ServerSelectionTimeoutError as e:
        raise RuntimeError("MongoDB ping failed (URI / IP allowlist / network)") from e

    return client


def disconnect_mongo(client: MongoClient) -> None:
    client.close()


def get_db_name() -> str:
    return os.getenv("MONGODB_DB")
