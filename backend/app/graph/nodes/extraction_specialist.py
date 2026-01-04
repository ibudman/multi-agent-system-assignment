from app.graph.state import GraphState


def extraction_specialist(state: GraphState) -> GraphState:
    leads = state.get("raw_leads") or []
    if not leads:
        return {"warnings": ["Extraction Specialist: raw_leads is empty (unexpected)."]}

    # TODO:
    # 1) select top N leads
    # 2) Tavily extract -> OpenAI structured output
    # 3) validate -> ProgramRecordGraph
    extracted = []
    warnings = []

    if not extracted:
        warnings.append("Extraction Specialist: No programs extracted.")

    updates: GraphState = {"extracted_programs": extracted}
    if warnings:
        updates["warnings"] = warnings
    return updates
