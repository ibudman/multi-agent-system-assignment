from typing import List, Literal, Optional
from pydantic import BaseModel, Field, AnyUrl

ProgramFormat = Literal["online", "in-person", "hybrid", "Not specified"]


class ProgramRecordBase(BaseModel):
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
