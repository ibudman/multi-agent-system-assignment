from app.graph.build import build_graph
from app.graph.state import create_initial_state, InputPayload, GraphState


_graph = build_graph()


def run_graph(request_id: str, payload: InputPayload) -> GraphState:
    initial_state = create_initial_state(request_id=request_id, payload=payload)
    return _graph.invoke(initial_state)
