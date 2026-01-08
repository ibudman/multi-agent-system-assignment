from dataclasses import dataclass
from typing import Optional
from app.external.protocols import OpenAIClientProtocol, TavilyClientProtocol


@dataclass
class GraphDeps:
    openai_client: Optional[OpenAIClientProtocol] = None
    tavily_client: Optional[TavilyClientProtocol] = None
