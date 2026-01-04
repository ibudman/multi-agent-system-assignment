# app/graph/state.py
from __future__ import annotations
from typing import TypedDict, Optional, List, Literal, Dict, Any

PrefsFormat = Literal["online", "in-person", "hybrid"]
PrefsGoal = Literal["hobby", "career", "skill improvement"]
PrefsBudget = Literal["free", "low-cost", "paid"]


class InputPrefs(TypedDict, total=False):
    format: Optional[PrefsFormat]
    goal: Optional[PrefsGoal]
    budget: Optional[PrefsBudget]
    city: Optional[str]


class InputPayload(TypedDict, total=False):
    query: str
    prefs: InputPrefs


class RawLead(TypedDict, total=False):
    url: str
    title: Optional[str]
    snippet: Optional[str]
    source: Optional[str]


class GraphState(TypedDict, total=False):
    request_id: str
    input: InputPayload

    raw_leads: List[RawLead]
    extracted_programs: List[Dict[str, Any]]  # replace with Program later if you want
    results: Dict[str, Any]  # {"short_term": [...], ...}
    warnings: List[str]

    status: Literal["running", "succeeded", "failed"]
    error: Optional[str]


def ensure_defaults(state: GraphState) -> GraphState:
    return {
        **state,
        "raw_leads": state.get("raw_leads", []),
        "extracted_programs": state.get("extracted_programs", []),
        "results": state.get(
            "results", {"short_term": [], "medium_term": [], "long_term": []}
        ),
        "warnings": state.get("warnings", []),
        "status": state.get("status", "running"),
        "error": state.get("error"),
    }
