from langgraph.graph import StateGraph, START, END
from app.graph.state import GraphState
from app.graph.nodes import adaptive_scout, extraction_specialist, path_organizer


def _after_scout(state: GraphState):
    return "extract" if state.get("raw_leads") else END


def build_graph():
    builder = StateGraph(GraphState)

    builder.add_node("scout", adaptive_scout)
    builder.add_node("extract", extraction_specialist)
    builder.add_node("organize", path_organizer)

    builder.add_edge(START, "scout")

    builder.add_conditional_edges(
        "scout",
        _after_scout,
        {"extract": "extract", END: END},
    )

    builder.add_edge("extract", "organize")
    builder.add_edge("organize", END)

    return builder.compile()
