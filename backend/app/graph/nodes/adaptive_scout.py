from app.graph.state import GraphState


def adaptive_scout(state: GraphState) -> GraphState:
    inp = state.get("input") or {}
    query = inp.get("query")
    prefs = inp.get("prefs")

    if not query:
        return {"warnings": ["Adaptive Scout: Missing input.query."]}

    # TODO:
    # 1) build 2–3 search queries from query + prefs
    # 2) call Tavily search
    # 3) map to RawLead list
    new_leads = []
    warnings = []

    if not new_leads:
        warnings.append("Adaptive Scout: No relevant learning leads found.")

    updates: GraphState = {"raw_leads": new_leads}
    if warnings:
        updates["warnings"] = warnings
    return updates
