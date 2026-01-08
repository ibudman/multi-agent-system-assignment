import pytest
import uuid
from app.db.models import RequestDoc, Paths
from app.graph.state import ProgramRecordGraph, GraphState, InputPayload
from app.models.schemas import Program, LearningPathsRequest, LearningPrefs
from app.services.learning_paths import LearningPathsService


class DummyRequestsRepo:
    def __init__(self):
        self.created = []
        self.completed = []
        self.failed = []

    def create_running(self, doc: RequestDoc):
        self.created.append(doc)

    def mark_completed(self, request_id: str):
        self.completed.append(request_id)

    def mark_failed(self, request_id: str, error: str):
        self.failed.append((request_id, error))


class DummyResultsRepo:
    def __init__(self):
        self.upserts = []

    def upsert_result(
        self, request_id: str, paths: Paths, warnings: list[str], error: str | None
    ):
        self.upserts.append(
            {
                "request_id": request_id,
                "paths": paths,
                "warnings": warnings,
                "error": error,
            }
        )


class DummyAgentRunsRepo:
    def __init__(self):
        pass

    def insert_run(self, doc: RequestDoc):
        pass


class FakeRunner:
    def __init__(self, *, state: GraphState = None, exc: Exception | None = None):
        self.state = state
        self.exc = exc
        self.calls = []

    def run(self, request_id: str, payload: InputPayload):
        self.calls.append(
            {
                "request_id": request_id,
                "payload": payload,
            }
        )

        if self.exc:
            raise self.exc

        return self.state


def expected_api_program_from_graph(p: ProgramRecordGraph) -> Program:
    return Program.model_validate(
        {
            "program_name": p.program_name,
            "provider": p.provider,
            "topics_covered": p.topics_covered,
            "format": p.format,
            "duration": p.duration,
            "cost": p.cost_text,
            "prerequisites": p.prerequisites,
            "location": p.location,
            "who_this_is_for": p.who_this_is_for,
            "source_link": p.source_link,
            "citation": p.citation,
        }
    )


# ---------- Tests ----------


# Verifies that the service correctly calls GraphRunner and returns the expected result when the runner completes successfully. (GraphRunner mocked)
def test_generate_happy_path():
    # --- Arrange ---
    requests_repo = DummyRequestsRepo()
    results_repo = DummyResultsRepo()
    agent_runs_repo = DummyAgentRunsRepo()

    program1 = ProgramRecordGraph(
        program_name="UX/UI Design Bootcamp",
        provider="Code Labs Academy",
        topics_covered=[
            "User experience research technique",
            "Competitor analysis",
            "Prototyping",
            "Information architecture",
            "Agile and Lean methodologies",
            "Figma",
            "Colour theory & typography",
        ],
        format="hybrid",
        duration="12 weeks",
        cost_usd=2500.0,
        cost_text="$2,500",
        prerequisites="No prerequisites or prior experience is required to attend.",
        location="San Francisco",
        who_this_is_for="Our program is designed to get you up to speed quickly and confidently.",
        source_link="https://www.reddit.com/r/UXDesign/comments/1kmrklq/freelance_ux_design_consulting_hourly_rate_for/",
        citation="https://www.reddit.com/r/UXDesign/comments/1kmrklq/freelance_ux_design_consulting_hourly_rate_for/",
    )
    program2 = ProgramRecordGraph(
        program_name="UX Design Classes & Bootcamps San Francisco",
        provider="Noble Desktop",
        topics_covered=[
            "UX design projects",
            "accessibility",
            "Figma",
            "usability testing",
            "prototyping",
            "wireframing",
        ],
        format="online",
        duration="Not specified",
        cost_usd=None,
        cost_text="Not specified",
        prerequisites="Not specified",
        location="Live Online from Anywhere",
        who_this_is_for="This program is for individuals looking to become UX/UI Designers.",
        source_link="https://www.nobledesktop.com/ux-design-classes-san-francisco",
        citation="https://www.nobledesktop.com/ux-design-classes-san-francisco",
    )

    fake_state: GraphState = {
        "results": {
            "short_term": [program2],
            "medium_term": [program1],
            "long_term": [],
        },
        "warnings": ["simulated warning"],
    }
    runner = FakeRunner(state=fake_state)

    service = LearningPathsService(
        requests_repo=requests_repo,
        agent_runs_repo=agent_runs_repo,
        results_repo=results_repo,
        runner=runner,
    )

    payload = LearningPathsRequest(
        query="ux design",
        prefs=LearningPrefs(
            format="in-person", goal="hobby", budget="paid", city="San Francisco"
        ),
    )

    # --- Act ---
    response = service.generate(payload)
    request_id_str = str(response.request_id)

    # --- Assert ---
    # 1) runner.run called once, with a request_id + payload
    assert len(runner.calls) == 1
    call = runner.calls[0]

    assert isinstance(call["request_id"], str)
    assert call["request_id"] == request_id_str

    # payload passed to runner is the InputPayload your service creates.
    # If your service passes the LearningPathsRequest directly, change this assert accordingly.
    assert call["payload"] == {
        "query": "ux design",
        "prefs": payload.prefs.model_dump(),
    }

    # 2) requests_repo.create_running captured one doc
    assert len(requests_repo.created) == 1
    created_doc = requests_repo.created[0]

    assert created_doc.request_id == request_id_str
    assert created_doc.status == "running"
    assert created_doc.input.query == "ux design"
    assert created_doc.input.prefs.model_dump() == payload.prefs.model_dump()

    # 3) results_repo.upsert_result called once with expected args
    assert len(results_repo.upserts) == 1
    upsert = results_repo.upserts[0]

    assert upsert["request_id"] == request_id_str

    paths = upsert["paths"]
    assert len(paths.short_term) == 1
    assert len(paths.medium_term) == 1
    assert len(paths.long_term) == 0

    assert upsert["warnings"] == ["simulated warning"]
    assert upsert["error"] is None

    # 4) requests_repo.mark_completed called with request_id
    assert requests_repo.completed == [request_id_str]

    # 5) response matches
    assert isinstance(response.request_id, uuid.UUID)
    assert response.results.short_term == [expected_api_program_from_graph(program2)]
    assert response.results.medium_term == [expected_api_program_from_graph(program1)]
    assert response.results.long_term == []
    assert response.warnings == ["simulated warning"]


# Verifies that the service properly handles a GraphRunner failure and returns the expected error or fallback response. (GraphRunner mocked)
def test_generate_runner_failure():
    # --- Arrange ---
    requests_repo = DummyRequestsRepo()
    results_repo = DummyResultsRepo()
    agent_runs_repo = DummyAgentRunsRepo()

    exc = RuntimeError("boom")
    runner = FakeRunner(exc=exc)

    service = LearningPathsService(
        requests_repo=requests_repo,
        agent_runs_repo=agent_runs_repo,
        results_repo=results_repo,
        runner=runner,
    )

    payload = LearningPathsRequest(
        query="ux design",
        prefs=LearningPrefs(
            format="in-person", goal="hobby", budget="paid", city="San Francisco"
        ),
    )

    # --- Act ---
    with pytest.raises(RuntimeError) as e:
        service.generate(payload)

    # --- Assert ---
    assert str(e.value) == "boom"

    # runner called once
    assert len(runner.calls) == 1
    call = runner.calls[0]
    assert call["payload"] == {
        "query": "ux design",
        "prefs": payload.prefs.model_dump(),
    }

    # create_running happened
    assert len(requests_repo.created) == 1
    created_doc = requests_repo.created[0]
    request_id_str = created_doc.request_id
    assert created_doc.status == "running"

    # results upserted with EMPTY + error message
    assert len(results_repo.upserts) == 1
    upsert = results_repo.upserts[0]
    assert upsert["request_id"] == request_id_str

    paths = upsert["paths"]
    assert len(paths.short_term) == 0
    assert len(paths.medium_term) == 0
    assert len(paths.long_term) == 0

    assert upsert["warnings"] == []
    assert upsert["error"] == "Generation failed. see requests.error for details."

    # mark_failed called with string request_id and exception string
    assert requests_repo.failed == [(request_id_str, "boom")]

    # no completion
    assert requests_repo.completed == []

    # runner request_id should match the one persisted
    assert call["request_id"] == request_id_str
