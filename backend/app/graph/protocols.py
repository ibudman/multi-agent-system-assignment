from typing import Protocol

from app.graph.state import InputPayload, GraphState


class GraphRunnerProtocol(Protocol):
    def run(self, request_id: str, payload: InputPayload) -> GraphState: ...
