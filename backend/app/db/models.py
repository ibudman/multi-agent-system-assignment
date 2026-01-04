from datetime import datetime
from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field
from app.models.base import ProgramRecordBase

# ---------- Shared types ----------

RequestStatus = Literal["running", "completed", "failed"]


# ---------- requests collection ----------


class RequestPrefs(BaseModel):
    format: Optional[Literal["online", "in-person", "hybrid"]] = None
    goal: Optional[Literal["hobby", "career", "skill improvement"]] = None
    budget: Optional[Literal["free", "low-cost", "paid"]] = None
    city: Optional[str] = None


class RequestInput(BaseModel):
    query: str
    prefs: Optional[RequestPrefs] = None


class RequestDoc(BaseModel):
    request_id: str
    created_at: datetime
    status: RequestStatus
    input: RequestInput
    error: Optional[str] = None


# ---------- agent_runs collection ----------


class AgentCounts(BaseModel):
    raw_leads: int = 0
    extracted_programs: int = 0


class AgentRunDoc(BaseModel):
    request_id: str
    agent_name: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    output_summary: Optional[Dict[str, Any]] = None
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# ---------- results collection ----------


class ProgramRecordDB(ProgramRecordBase):
    pass


class Paths(BaseModel):
    short_term: List[ProgramRecordDB] = Field(default_factory=list)
    medium_term: List[ProgramRecordDB] = Field(default_factory=list)
    long_term: List[ProgramRecordDB] = Field(default_factory=list)


class ResultDoc(BaseModel):
    request_id: str
    created_at: datetime
    paths: Paths = Field(default_factory=Paths)
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
