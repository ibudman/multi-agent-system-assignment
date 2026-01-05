from langgraph.graph import StateGraph, START, END
from functools import partial

from app.graph.deps import GraphDeps
from app.graph.state import GraphState
from app.graph.nodes import adaptive_scout, extraction_specialist, path_organizer


def _after_scout(state: GraphState):
    return "extract" if state.get("raw_leads") else END


def build_graph(deps: GraphDeps):
    builder = StateGraph(GraphState)

    builder.add_node("scout", partial(adaptive_scout, tavily_client=deps.tavily_client))
    builder.add_node(
        "extract",
        partial(
            extraction_specialist,
            tavily_client=deps.tavily_client,
            openai_client=deps.openai_client,
        ),
    )
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
