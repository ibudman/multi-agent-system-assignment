from tavily import TavilyClient
from typing import Optional
from app.graph.state import GraphState, InputPrefs, RawLead

MAX_SEARCH_QUERIES = 3
RESULTS_PER_QUERY = 6
MAX_LEADS_TOTAL = 12


def _build_queries(query: str, prefs: Optional[InputPrefs]) -> list[str]:
    boosters = []

    if prefs.get("format"):
        boosters.append(prefs["format"].replace("-", " "))
    if prefs.get("goal"):
        boosters.append(prefs["goal"])
    if prefs.get("budget"):
        boosters.append(prefs["budget"].replace("-", " "))
    if prefs.get("city"):
        boosters.append(prefs["city"])

    base_query = query.strip()

    search_queries = []
    q1 = " ".join([base_query] + boosters).strip()
    q2 = " ".join([base_query, "course program workshop bootcamp"] + boosters).strip()
    q3 = " ".join([base_query, "certificate curriculum syllabus"] + boosters).strip()

    for q in (q1, q2, q3):
        if q and q not in search_queries:
            search_queries.append(q)

    return search_queries[:MAX_SEARCH_QUERIES]


def adaptive_scout(state: GraphState, tavily_client: TavilyClient) -> GraphState:
    inp = state.get("input") or {}
    query = inp.get("query")
    prefs = inp.get("prefs")

    if not query:
        return {"warnings": ["Adaptive Scout: Missing input.query."]}

    # 1) build 2–3 search queries from query + prefs
    search_queries = _build_queries(query, prefs)

    # 2) call Tavily search
    warnings: list[str] = []
    raw_results = []
    for q in search_queries:
        try:
            res = tavily_client.search(
                query=q,
                max_results=RESULTS_PER_QUERY,
                search_depth="basic",
            )

            raw_results.extend(
                res.get("results") or []
            )  # [title, url, content, score, raw_content, favicon]
        except Exception as e:
            warnings.append(f"Adaptive Scout: Search failed for query '{q}' ({str(e)})")

    # 3) map to RawLead list
    new_leads: list[RawLead] = []
    seen_urls: set[str] = set()

    for res in raw_results:
        url = res.get("url")
        if url and url not in seen_urls:
            seen_urls.add(url)
            new_leads.append(
                {
                    "url": url,
                    "title": res.get("title"),
                    "snippet": res.get("content"),
                    "source": url.split("//")[-1].split("/")[0].replace("www.", ""),
                }
            )
            if len(new_leads) >= MAX_LEADS_TOTAL:
                break

    if not new_leads:
        warnings.append("Adaptive Scout: No relevant learning leads found.")

    updates: GraphState = {"raw_leads": new_leads}
    if warnings:
        updates["warnings"] = warnings
    return updates
