import re
from app.graph.state import GraphState, ResultsPayload, ProgramRecordGraph

MAX_PER_BUCKET = 5
MIN_TOTAL_PROGRAMS_WARNING = 3
SHORT_MAX_WEEKS = 4
MEDIUM_MAX_WEEKS = 24

LONG_TERM_KEYWORDS = (
    "degree",
    "university",
    "college",
    "bachelor",
    "master",
    "mba",
    "phd",
    "msc",
    "bsc",
    "m.sc",
    "b.sc",
    "semester",
    "year",
)
SHORT_TERM_KEYWORDS = (
    "workshop",
    "intro",
    "introduction",
    "crash",
    "bootcamp prep",
    "fundamentals",
    "basics",
    "webinar",
    "seminar",
    "one-day",
    "one day",
    "weekend",
    "short course",
    "intensive",
)


def _init_empty_results() -> ResultsPayload:
    return {"short_term": [], "medium_term": [], "long_term": []}


def _program_key(p: ProgramRecordGraph) -> str:
    return p.source_link.strip().lower()


def _parse_duration_weeks(duration: str | None) -> float | None:
    # duration to weeks when clearly specified; otherwise None
    s = (duration or "").strip().lower()
    if not s or s == "not specified":
        return None

    m = re.search(r"(\d+(?:\.\d+)?)\s*(day|days|week|weeks|month|months|year|years)", s)
    if not m:
        return None

    val = float(m.group(1))
    unit = m.group(2)

    if "day" in unit:
        return val / 7.0
    if "week" in unit:
        return val
    if "month" in unit:
        return val * 4.345
    if "year" in unit:
        return val * 52.0
    return None


def _bucket_from_duration_weeks(weeks: float) -> str:
    if weeks <= SHORT_MAX_WEEKS:
        return "short_term"
    if weeks <= MEDIUM_MAX_WEEKS:
        return "medium_term"
    return "long_term"


def _bucket_from_keywords(p: ProgramRecordGraph) -> str:
    # Fallback heuristic when duration is missing/unclear
    text = f"{p.provider.lower()} {p.program_name.lower()}"
    if any(w in text for w in LONG_TERM_KEYWORDS):
        return "long_term"
    if any(w in text for w in SHORT_TERM_KEYWORDS):
        return "short_term"
    return "medium_term"


def _add_to_bucket(
    results: ResultsPayload, bucket: str, program: ProgramRecordGraph
) -> bool:
    # Returns True if added, False if dropped due to per-bucket limit
    if len(results[bucket]) < MAX_PER_BUCKET:
        results[bucket].append(program)
        return True
    return False


def _all_buckets_full(results: ResultsPayload) -> bool:
    return all(len(results[b]) >= MAX_PER_BUCKET for b in results)


def path_organizer(state: GraphState) -> GraphState:
    programs: list[ProgramRecordGraph] = state.get("extracted_programs") or []

    empty_results: ResultsPayload = _init_empty_results()

    if not programs:
        return {
            "results": empty_results,
            "warnings": ["Path Organizer: No programs were available to categorize."],
        }

    results: ResultsPayload = _init_empty_results()
    warnings: list[str] = []

    # 1) bucket into short_term / medium_term / long_term
    #    - Prefer duration when clearly specified
    #    - Otherwise, use provider/title keyword heuristics (and warn)
    # 2) enforce no duplicates across buckets
    #    - Global dedupe (by URL, else provider+title) before inserting
    # 3) apply max per bucket
    #    - Drop overflow items per bucket and warn

    seen_keys: set[str] = set()
    dup_count = 0
    used_fallback = 0
    dropped_due_to_limits = 0

    for p in programs:
        # (2) Deduplicate
        key = _program_key(p)
        if key in seen_keys:
            dup_count += 1
            continue
        seen_keys.add(key)

        # (1) Choose bucket
        weeks = _parse_duration_weeks(p.duration)
        if weeks is not None:
            bucket = _bucket_from_duration_weeks(weeks)
        else:
            bucket = _bucket_from_keywords(p)
            used_fallback += 1

        # (3) Add with per-bucket limit
        if not _add_to_bucket(results, bucket, p):
            dropped_due_to_limits += 1

        # Stop early if all buckets are full
        if _all_buckets_full(results):
            break

    if dup_count:
        warnings.append(
            f"Path Organizer: Removed {dup_count} duplicate program(s) before bucketing."
        )
    if used_fallback:
        warnings.append(
            f"Path Organizer: Bucketing used fallback heuristics for {used_fallback} program(s) due to missing duration."
        )
    if dropped_due_to_limits:
        warnings.append(
            f"Path Organizer: Dropped {dropped_due_to_limits} program(s) due to per-bucket limit ({MAX_PER_BUCKET})."
        )

    empties = [b for b, items in results.items() if not items]
    if empties:
        warnings.append(
            f"Path Organizer: One or more buckets are empty: {', '.join(empties)}."
        )

    total = sum(len(v) for v in results.values())
    if total < MIN_TOTAL_PROGRAMS_WARNING:
        warnings.append(
            f"Path Organizer: Low number of programs after categorization (total={total})."
        )

    updates: GraphState = {"results": results}
    if warnings:
        updates["warnings"] = warnings
    return updates
