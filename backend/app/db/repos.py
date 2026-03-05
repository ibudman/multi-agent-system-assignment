from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional
from pymongo.collection import Collection

from app.db.models import RequestDoc, AgentRunDoc, Paths, CacheDoc


@dataclass
class RequestsRepo:
    col: Collection

    def create_running(self, doc: RequestDoc) -> None:
        self.col.insert_one(doc.model_dump())

    def mark_completed(self, request_id: str) -> None:
        self.col.update_one(
            {"request_id": request_id}, {"$set": {"status": "completed"}}
        )

    def mark_failed(self, request_id: str, error: str) -> None:
        self.col.update_one(
            {"request_id": request_id}, {"$set": {"status": "failed", "error": error}}
        )


@dataclass
class AgentRunsRepo:
    col: Collection

    def insert_run(self, doc: AgentRunDoc) -> None:
        self.col.insert_one(doc.model_dump())


@dataclass
class ResultsRepo:
    col: Collection

    def upsert_result(
        self, request_id: str, paths: Paths, warnings: list[str], error: str | None
    ) -> None:
        self.col.update_one(
            {"request_id": request_id},
            {
                "$set": {
                    "request_id": request_id,
                    "created_at": datetime.now(timezone.utc),
                    "paths": paths.model_dump(mode="json"),
                    "warnings": warnings,  # full-request warnings (final)
                    "error": error,
                }
            },
            upsert=True,
        )


@dataclass
class CacheRepo:
    col: Collection

    def get(self, cache_key: str) -> CacheDoc | None:
        doc = self.col.find_one({"cache_key": cache_key}, {"_id": 0})
        if doc:
            return CacheDoc.model_validate(doc)
        return None

    def set(self, doc: CacheDoc) -> None:
        self.col.update_one(
            {"cache_key": doc.cache_key},
            {"$set": doc.model_dump(mode="json")},
            upsert=True,
        )
