from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, AnyUrl


# ---------- Shared types ----------

RequestStatus = Literal["running", "completed", "failed"]
ProgramFormat = Literal["online", "in-person", "hybrid", "Not specified"]


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


class AgentOutputSummary(BaseModel):
    counts: AgentCounts = Field(default_factory=AgentCounts)
    selected_urls: List[AnyUrl] = Field(default_factory=list)


class AgentRunDoc(BaseModel):
    request_id: UUID
    agent_name: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    output_summary: Optional[AgentOutputSummary] = None
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None


# ---------- results collection ----------


class Program(BaseModel):
    program_name: str
    provider: str
    topics_covered: List[str] = Field(default_factory=list)
    format: ProgramFormat = "Not specified"
    duration: str = "Not specified"
    cost_usd: Optional[float] = None
    cost_text: str = "Not specified"
    prerequisites: str = "Not specified"
    location: str = "Not specified"
    who_this_is_for: str = "Not specified"
    source_link: AnyUrl
    citation: AnyUrl


class Paths(BaseModel):
    short_term: List[Program] = Field(default_factory=list)
    medium_term: List[Program] = Field(default_factory=list)
    long_term: List[Program] = Field(default_factory=list)


class ResultDoc(BaseModel):
    request_id: UUID
    created_at: datetime
    paths: Paths = Field(default_factory=Paths)
    warnings: List[str] = Field(default_factory=list)
    error: Optional[str] = None
