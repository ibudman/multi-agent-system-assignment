from typing import Protocol
from app.db.models import RequestDoc, Paths


class RequestsRepoProtocol(Protocol):
    def create_running(self, doc: RequestDoc) -> None: ...
    def mark_completed(self, request_id: str) -> None: ...
    def mark_failed(self, request_id: str, error: str) -> None: ...


class ResultsRepoProtocol(Protocol):
    def upsert_result(
        self, request_id: str, paths: Paths, warnings: list[str], error: str | None
    ) -> None: ...


class AgentRunsRepoProtocol(Protocol):
    def insert_run(self, doc: RequestDoc) -> None: ...
