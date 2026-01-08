from typing import Any, Protocol, Type
from openai.types.responses import ParsedResponse

from app.graph.state import ProgramRecordGraph


class OpenAIResponsesProtocol(Protocol):

    def parse(
        self,
        *,
        model: str,
        temperature: float = 0,
        input: str | list[dict[str, Any]],
        text_format: Type[ProgramRecordGraph],
        max_output_tokens: int | None = None,
        **kwargs: Any,
    ) -> ParsedResponse[ProgramRecordGraph]: ...


class OpenAIClientProtocol(Protocol):
    responses: OpenAIResponsesProtocol


class TavilyClientProtocol(Protocol):
    def search(
        self, query: str, max_results: int | None = None, **kwargs: Any
    ) -> dict[str, Any]: ...
    def extract(
        self, urls: str | list[str], extract_depth: str | None = None, **kwargs: Any
    ) -> dict[str, Any]: ...
