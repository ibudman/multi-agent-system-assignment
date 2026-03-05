import hashlib
import json
import logging

logger = logging.getLogger(__name__)
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.db.models import RequestDoc, RequestInput, Paths, ProgramRecordDB, CacheDoc
from app.db.protocols import (
    RequestsRepoProtocol,
    ResultsRepoProtocol,
    AgentRunsRepoProtocol,
    CacheRepoProtocol,
)
from app.graph.protocols import GraphRunnerProtocol
from app.graph.state import ProgramRecordGraph, ResultsPayload, GraphState
from app.models.schemas import (
    LearningPathsRequest,
    LearningPathsResponse,
    LearningPathsResults,
    Program,
)


EMPTY_PATHS: ResultsPayload = {"short_term": [], "medium_term": [], "long_term": []}


def _make_cache_key(query: str, prefs: dict | None) -> str:
    payload = {
        "query": query.lower().strip(),
        "prefs": dict(sorted((prefs or {}).items())),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def results_payload_to_paths(results: ResultsPayload) -> Paths:
    def to_db(p: ProgramRecordGraph) -> ProgramRecordDB:
        return ProgramRecordDB.model_validate(p.model_dump())

    return Paths(
        short_term=[to_db(p) for p in results.get("short_term", [])],
        medium_term=[to_db(p) for p in results.get("medium_term", [])],
        long_term=[to_db(p) for p in results.get("long_term", [])],
    )


def _paths_to_learning_paths_results(paths: Paths) -> LearningPathsResults:
    def to_program(p: ProgramRecordDB) -> Program:
        return Program.model_validate(
            {
                "program_name": p.program_name,
                "provider": p.provider,
                "topics_covered": p.topics_covered,
                "format": p.format,
                "duration": p.duration,
                "cost": p.cost_text,
                "prerequisites": p.prerequisites,
                "location": p.location,
                "who_this_is_for": p.who_this_is_for,
                "source_link": p.source_link,
                "citation": p.citation,
            }
        )

    return LearningPathsResults(
        short_term=[to_program(p) for p in paths.short_term],
        medium_term=[to_program(p) for p in paths.medium_term],
        long_term=[to_program(p) for p in paths.long_term],
    )


def results_payload_to_learning_paths_results(
    results: ResultsPayload,
) -> LearningPathsResults:

    def to_program(p: ProgramRecordGraph) -> Program:
        return Program.model_validate(
            {
                "program_name": p.program_name,
                "provider": p.provider,
                "topics_covered": p.topics_covered,
                "format": p.format,
                "duration": p.duration,
                "cost": p.cost_text,
                "prerequisites": p.prerequisites,
                "location": p.location,
                "who_this_is_for": p.who_this_is_for,
                "source_link": p.source_link,  # str -> HttpUrl
                "citation": p.citation,
            }
        )

    return LearningPathsResults(
        short_term=[to_program(p) for p in results.get("short_term", [])],
        medium_term=[to_program(p) for p in results.get("medium_term", [])],
        long_term=[to_program(p) for p in results.get("long_term", [])],
    )


@dataclass
class LearningPathsService:
    requests_repo: RequestsRepoProtocol
    agent_runs_repo: AgentRunsRepoProtocol
    results_repo: ResultsRepoProtocol
    runner: GraphRunnerProtocol
    cache_repo: CacheRepoProtocol

    def generate(self, payload: LearningPathsRequest) -> LearningPathsResponse:
        request_id = uuid.uuid4()
        request_id_str = str(request_id)
        prefs_dict = payload.prefs.model_dump() if payload.prefs else None
        cache_key = _make_cache_key(payload.query, prefs_dict)

        logger.info(
            "learning_paths_start. request_id=%s query_len=%s",
            request_id_str,
            len(payload.query),
        )

        # --- Cache lookup ---
        cached = self.cache_repo.get(cache_key)
        if cached is not None:
            logger.info("learning_paths_cache_hit. request_id=%s", request_id_str)
            doc = RequestDoc(
                request_id=request_id_str,
                created_at=datetime.now(timezone.utc),
                status="completed",
                input=RequestInput(query=payload.query, prefs=prefs_dict),
                error=None,
            )
            self.requests_repo.create_running(doc)
            self.requests_repo.mark_completed(request_id=request_id_str)

            cached_results = _paths_to_learning_paths_results(cached.paths)
            return LearningPathsResponse(
                request_id=request_id,
                results=cached_results,
                warnings=cached.warnings,
                cache_hit=True,
            )

        # --- Cache miss: run the graph ---
        doc = RequestDoc(
            request_id=request_id_str,
            created_at=datetime.now(timezone.utc),
            status="running",
            input=RequestInput(query=payload.query, prefs=prefs_dict),
            error=None,
        )
        self.requests_repo.create_running(doc)

        try:
            final_state: GraphState = self.runner.run(
                request_id=request_id_str,
                payload={"query": payload.query, "prefs": prefs_dict},
            )

            final_state_results: ResultsPayload = (
                final_state.get("results") or EMPTY_PATHS
            )
            results: LearningPathsResults = results_payload_to_learning_paths_results(
                final_state_results
            )

            warnings: list[str] = final_state.get("warnings", [])
            paths = results_payload_to_paths(final_state_results)

            self.results_repo.upsert_result(
                request_id=request_id_str,
                paths=paths,
                warnings=warnings,
                error=None,
            )
            self.requests_repo.mark_completed(request_id=request_id_str)

            self.cache_repo.set(
                CacheDoc(
                    cache_key=cache_key,
                    cached_at=datetime.now(timezone.utc),
                    paths=paths,
                    warnings=warnings,
                )
            )

            logger.info(
                "learning_paths_done. request_id=%s short=%d medium=%d long=%d warnings=%d",
                request_id_str,
                len(results.short_term),
                len(results.medium_term),
                len(results.long_term),
                len(warnings),
            )

            return LearningPathsResponse(
                request_id=request_id, results=results, warnings=warnings
            )

        except Exception as e:
            logger.exception("learning_paths_failed. request_id=%s", request_id_str)

            self.results_repo.upsert_result(
                request_id=request_id_str,
                paths=results_payload_to_paths(EMPTY_PATHS),
                warnings=[],
                error="Generation failed. see requests.error for details.",
            )
            self.requests_repo.mark_failed(request_id=request_id_str, error=str(e))
            raise
