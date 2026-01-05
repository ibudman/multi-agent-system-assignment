from dataclasses import dataclass
from typing import Optional
from openai import OpenAI
from tavily import TavilyClient


@dataclass
class GraphDeps:
    openai_client: Optional[OpenAI] = None
    tavily_client: Optional[TavilyClient] = None
