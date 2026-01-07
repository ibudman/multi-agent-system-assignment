import operator
from typing import TypedDict, Optional, List, Literal, Annotated
from app.models.base import ProgramRecordBase

PrefsFormat = Literal["online", "in-person", "hybrid"]
PrefsGoal = Literal["hobby", "career", "skill improvement"]
PrefsBudget = Literal["free", "low-cost", "paid"]


class InputPrefs(TypedDict, total=False):
    format: Optional[PrefsFormat]
    goal: Optional[PrefsGoal]
    budget: Optional[PrefsBudget]
    city: Optional[str]


class InputPayload(TypedDict):
    query: str
    prefs: Optional[InputPrefs]


class RawLead(TypedDict, total=False):
    url: str
    title: Optional[str]
    snippet: Optional[str]
    source: Optional[str]


class ProgramRecordGraph(ProgramRecordBase):
    pass


class ResultsPayload(TypedDict):
    short_term: List[ProgramRecordGraph]
    medium_term: List[ProgramRecordGraph]
    long_term: List[ProgramRecordGraph]


class GraphState(TypedDict, total=False):
    request_id: str
    input: InputPayload
    # reducers: nodes return partial updates that get appended/merged
    raw_leads: Annotated[List[RawLead], operator.add]
    extracted_programs: Annotated[List[ProgramRecordGraph], operator.add]
    warnings: Annotated[List[str], operator.add]
    # organizer overwrites this whole object
    results: ResultsPayload


def create_initial_state(request_id: str, payload: InputPayload) -> GraphState:
    return {
        "request_id": request_id,
        "input": payload,
        "raw_leads": [],
        "extracted_programs": [],
        "results": {"short_term": [], "medium_term": [], "long_term": []},
        "warnings": [],
    }
