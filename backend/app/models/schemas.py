from typing import List, Optional, Literal
from uuid import UUID
from pydantic import BaseModel, HttpUrl, Field, field_validator


class HealthCheckResponse(BaseModel):
    status: str


Format = Literal["online", "in-person", "hybrid"]
Goal = Literal["hobby", "career", "skill improvement"]
Budget = Literal["free", "low-cost", "paid"]


class LearningPrefs(BaseModel):
    format: Optional[Format] = None
    goal: Optional[Goal] = None
    budget: Optional[Budget] = None
    city: Optional[str] = None


class LearningPathsRequest(BaseModel):
    query: str
    prefs: Optional[LearningPrefs] = None

    @field_validator("query")
    @classmethod
    def query_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("query must not be empty")
        return v


ProgramFormat = Literal["online", "in-person", "hybrid", "Not specified"]


class Program(BaseModel):
    program_name: str
    provider: str
    topics_covered: List[str] = Field(default_factory=list)
    format: ProgramFormat = "Not specified"
    duration: str = "Not specified"
    cost: str = "Not specified"
    prerequisites: str = "Not specified"
    location: str = "Not specified"
    who_this_is_for: str = "Not specified"
    source_link: HttpUrl
    citation: HttpUrl


class LearningPathsResults(BaseModel):
    short_term: List[Program] = Field(default_factory=list)
    medium_term: List[Program] = Field(default_factory=list)
    long_term: List[Program] = Field(default_factory=list)


class LearningPathsResponse(BaseModel):
    request_id: UUID
    results: LearningPathsResults
    warnings: List[str] = Field(default_factory=list)
