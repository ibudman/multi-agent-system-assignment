import re

from app.external.protocols import TavilyClientProtocol, OpenAIClientProtocol
from app.graph.state import GraphState, ProgramRecordGraph, RawLead


MAX_URLS_TO_EXTRACT = 10
LLM_TOKEN_LIMIT_PER_PAGE = 1800
MAX_CHARS_PER_PAGE = LLM_TOKEN_LIMIT_PER_PAGE * 4


def _dedupe_and_select_urls(leads: list[RawLead], max_urls: int) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for lead in leads:
        url = lead.get("url")
        if not isinstance(url, str) or not url:
            continue
        if url in seen:
            continue
        seen.add(url)
        out.append(url)
        if len(out) >= max_urls:
            break
    return out


def _extract_pages(
    tavily_client: TavilyClientProtocol, urls: list[str]
) -> tuple[dict[str, str], list[str]]:
    url_to_text: dict[str, str] = {}
    warnings: list[str] = []

    if not urls:
        return {}, []
    res = tavily_client.extract(urls=urls, extract_depth="basic")

    if not isinstance(res, dict):
        return {}, [
            "Extraction Specialist: Tavily extract returned unexpected response type."
        ]

    results = res.get("results") or []  # [url, raw_content]
    if isinstance(results, list):
        for item in results:
            if not isinstance(item, dict):
                continue
            u = item.get("url")
            if not u:
                continue
            txt = (item.get("raw_content") or "").strip()
            if txt:
                url_to_text[u] = txt
            else:
                warnings.append(
                    f"Extraction Specialist: Tavily extract returned empty content for {u}"
                )

    failed_results = res.get("failed_results") or []  # [url, error]
    if isinstance(failed_results, list):
        for item in failed_results:
            if not isinstance(item, dict):
                continue
            u = item.get("url") or "Unknown URL"
            err = item.get("error") or "Unknown error"
            warnings.append(
                f"Extraction Specialist: Tavily extract failed for {u} ({err})"
            )

    return url_to_text, warnings


def _truncate_for_llm(text: str, max_chars: int) -> str:
    if not text:
        return ""
    text = text.strip()
    if len(text) <= max_chars:
        return text

    head_len = int(max_chars * 0.7)
    tail_len = max_chars - head_len - 3  # "..."

    return text[:head_len] + "..." + text[-tail_len:]


_SYSTEM_PROMPT = """
Extract a single ProgramRecord JSON object from the provided webpage text.

Global rules:
- Use ONLY information explicitly stated in the text. Do NOT guess.
- If a field is missing/unclear, set it to exactly "Not specified" (except cost_usd may be null).
- Output ONLY valid JSON with exactly these keys (no extras, no omissions):

program_name: string
provider: string
topics_covered: string[]
format: string
duration: string
cost_usd: number|null
cost_text: string
prerequisites: string
location: string
who_this_is_for: string
source_link: string
citation: string

Field rules:
- topics_covered: 3–8 concise topics explicitly mentioned (or [] if none).
- who_this_is_for: 1 short sentence based only on explicit wording.
- format: output ONLY one of "online", "in-person", "hybrid", "Not specified".
  Map common variants: remote/virtual/zoom -> online; in person -> in-person.
- cost:
  - If no explicit price: cost_text="Not specified", cost_usd=null.
  - If price exists: cost_text should quote the page's pricing wording.
  - Set cost_usd ONLY if an explicit numeric USD amount is stated (e.g., "$1200" or "1200 USD"); otherwise null.
- source_link and citation: always set both to the provided URL exactly.
""".strip()


def _llm_program_record(
    openai_client: OpenAIClientProtocol, url: str, page_text: str
) -> dict:
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": str(_SYSTEM_PROMPT)},
        {"role": "user", "content": f"URL: {url}\n\nText:\n{page_text}"},
    ]

    resp = openai_client.responses.parse(
        model="gpt-4o-mini",
        temperature=0,  # ensure deterministic output
        input=messages,
        text_format=ProgramRecordGraph,
        max_output_tokens=600,
    )

    parsed = getattr(resp, "output_parsed", None) or resp.output[0].parsed

    return parsed.model_dump()


_USD_RE = re.compile(r"\$?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(USD|usd|\$)?")


def _explicit_usd(cost_text: str) -> float | None:
    if not cost_text or cost_text.strip().lower() == "not specified":
        return None
    m = _USD_RE.search(cost_text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", ""))
    except ValueError:
        return None


def _enforce_invariants(rec: dict, url: str) -> dict:
    cost_text = rec.get("cost_text")
    if not isinstance(cost_text, str) or cost_text.strip().lower() == "not specified":
        rec["cost_text"] = "Not specified"
        rec["cost_usd"] = None
    else:
        rec["cost_usd"] = _explicit_usd(cost_text)

    rec["source_link"] = url
    rec["citation"] = url
    return rec


def extraction_specialist(
    state: GraphState,
    tavily_client: TavilyClientProtocol,
    openai_client: OpenAIClientProtocol,
) -> GraphState:
    leads = state.get("raw_leads") or []
    if not leads:
        return {"warnings": ["Extraction Specialist: raw_leads is empty (unexpected)."]}

    # 1) select top N leads
    selected_urls = _dedupe_and_select_urls(leads, MAX_URLS_TO_EXTRACT)
    if not selected_urls:
        return {
            "warnings": ["Extraction Specialist: No valid URLs found in raw_leads."]
        }

    # 2) Tavily extract -> OpenAI structured output
    extracted: list[ProgramRecordGraph] = []
    warnings: list[str] = []
    # 2) Tavily batch extract
    try:
        url_to_text, extract_warnings = _extract_pages(tavily_client, selected_urls)
        warnings.extend(extract_warnings)
    except Exception as e:
        warnings.append(
            f"Extraction Specialist: Tavily batch extract failed ({str(e)})"
        )
        url_to_text = {}

    # 3) OpenAI per URL -> structured output -> validate ProgramRecordGraph
    for url in selected_urls:
        page_text = (url_to_text.get(url) or "").strip()
        if not page_text:
            continue

        try:
            # fit content into token budget
            page_text = _truncate_for_llm(page_text, MAX_CHARS_PER_PAGE)
            # mapping text → structured ProgramRecord + Enforce no-guessing
            rec_dict = _llm_program_record(openai_client, url, page_text)
            #  normalize + set source_link/citation
            rec_dict = _enforce_invariants(rec_dict, url)
            program = ProgramRecordGraph.model_validate(rec_dict)
            extracted.append(program)
        except Exception as e:
            warnings.append(f"Extraction Specialist: Failed for {url} ({str(e)})")
            continue

    if not extracted:
        warnings.append("Extraction Specialist: No programs extracted.")

    updates: GraphState = {"extracted_programs": extracted}
    if warnings:
        updates["warnings"] = warnings
    return updates
