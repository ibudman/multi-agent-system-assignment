from app.graph.state import GraphState, ResultsPayload


def path_organizer(state: GraphState) -> GraphState:
    programs = state.get("extracted_programs") or []

    empty_results: ResultsPayload = {
        "short_term": [],
        "medium_term": [],
        "long_term": [],
    }

    if not programs:
        return {
            "results": empty_results,
            "warnings": ["Path Organizer: No programs were available to categorize."],
        }

    # TODO:
    # 1) bucket into short_term / medium_term / long_term
    # 2) enforce no duplicates across buckets
    # 3) apply max per bucket
    results: ResultsPayload = {"short_term": [], "medium_term": [], "long_term": []}
    warnings = []

    updates: GraphState = {"results": results}
    if warnings:
        updates["warnings"] = warnings
    return updates
