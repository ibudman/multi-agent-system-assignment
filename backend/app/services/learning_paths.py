import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

from app.db.models import RequestDoc, RequestInput, Paths, ProgramRecordDB
from app.db.protocols import (
    RequestsRepoProtocol,
    ResultsRepoProtocol,
    AgentRunsRepoProtocol,
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


def results_payload_to_paths(results: ResultsPayload) -> Paths:
    def to_db(p: ProgramRecordGraph) -> ProgramRecordDB:
        return ProgramRecordDB.model_validate(p.model_dump())

    return Paths(
        short_term=[to_db(p) for p in results.get("short_term", [])],
        medium_term=[to_db(p) for p in results.get("medium_term", [])],
        long_term=[to_db(p) for p in results.get("long_term", [])],
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

    def generate(self, payload: LearningPathsRequest) -> LearningPathsResponse:
        request_id = uuid.uuid4()
        request_id_str = str(request_id)

        doc = RequestDoc(
            request_id=request_id_str,
            created_at=datetime.now(timezone.utc),
            status="running",
            input=RequestInput(
                query=payload.query,
                prefs=(payload.prefs.model_dump() if payload.prefs else None),
            ),
            error=None,
        )
        self.requests_repo.create_running(doc)

        try:
            final_state: GraphState = self.runner.run(
                request_id=request_id_str,
                payload={
                    "query": payload.query,
                    "prefs": payload.prefs.model_dump() if payload.prefs else None,
                },
            )

            final_state_results: ResultsPayload = (
                final_state.get("results") or EMPTY_PATHS
            )
            results: LearningPathsResults = results_payload_to_learning_paths_results(
                final_state_results
            )

            warnings: list[str] = final_state.get("warnings", [])

            self.results_repo.upsert_result(
                request_id=request_id_str,
                paths=results_payload_to_paths(final_state_results),
                warnings=warnings,
                error=None,
            )
            self.requests_repo.mark_completed(request_id=request_id_str)

            return LearningPathsResponse(
                request_id=request_id, results=results, warnings=warnings
            )

        except Exception as e:
            self.results_repo.upsert_result(
                request_id=request_id_str,
                paths=results_payload_to_paths(EMPTY_PATHS),
                warnings=[],
                error="Generation failed",
            )
            self.requests_repo.mark_failed(request_id=request_id_str, error=str(e))
            raise
