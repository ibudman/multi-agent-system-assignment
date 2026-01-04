from datetime import datetime, timezone
from typing import Dict, Any
from dataclasses import dataclass

from app.db.models import AgentRunDoc
from app.db.repos import AgentRunsRepo
from app.graph.build import build_graph
from app.graph.state import create_initial_state, InputPayload, GraphState


_LIST_ACCUM_KEYS = {"raw_leads", "extracted_programs", "warnings"}


def _merge_for_snapshot(
    snapshot: Dict[str, Any], delta: Dict[str, Any]
) -> Dict[str, Any]:
    merged = dict(snapshot)
    for k, v in delta.items():
        if k in _LIST_ACCUM_KEYS:
            merged[k] = (merged.get(k, []) or []) + (v or [])
        else:
            merged[k] = v
    return merged


def _output_summary(node_name: str, snapshot: Dict[str, Any]) -> dict:
    summary: dict = {
        "counts": {
            "raw_leads": len(snapshot.get("raw_leads", [])),
            "extracted_programs": len(snapshot.get("extracted_programs", [])),
        }
    }

    if node_name == "scout":
        summary["selected_urls"] = [
            x.get("url") for x in snapshot.get("raw_leads", []) if isinstance(x, dict)
        ][:10]

    if node_name == "organize":
        results = snapshot.get("results") or {}
        summary["bucket_counts"] = {
            "short_term": len(results.get("short_term", [])),
            "medium_term": len(results.get("medium_term", [])),
            "long_term": len(results.get("long_term", [])),
        }

    return summary


@dataclass
class GraphRunner:
    agent_runs_repo: AgentRunsRepo
    graph: Any = None

    def __post_init__(self) -> None:
        self.graph = self.graph or build_graph()

    def run(self, request_id: str, payload: InputPayload) -> GraphState:
        # Initialize State
        initial_state = create_initial_state(
            request_id=str(request_id), payload=payload
        )
        snapshot: Dict[str, Any] = dict(initial_state)
        # Track timing for the first node
        last_step_time = datetime.now(timezone.utc)

        # Stream the execution
        # event is a dict: { "node_name": { "delta_key": "delta_value" }
        for event in self.graph.stream(initial_state, stream_mode="updates"):
            started_at = last_step_time
            ended_at = datetime.now(timezone.utc)
            last_step_time = ended_at

            node_name, delta = next(iter(event.items()))

            # STEP-ONLY warnings: only what THIS node returned
            step_warnings = delta.get("warnings") or []
            if not isinstance(step_warnings, list):
                step_warnings = [str(step_warnings)]

            # Merge delta into snapshot so output_summary can reflect latest state
            snapshot = _merge_for_snapshot(snapshot, delta)

            doc = AgentRunDoc(
                request_id=request_id,
                agent_name=node_name,
                started_at=started_at,
                ended_at=ended_at,
                output_summary=_output_summary(node_name, snapshot),
                warnings=step_warnings,
                error=None,  # TODO: check
            )

            self.agent_runs_repo.insert_run(doc)

        return snapshot  # final state
