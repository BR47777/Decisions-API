from types import SimpleNamespace

from fastapi.testclient import TestClient

from app.main import DecisionUpstreamError, create_app


def _action(**context):
    return {
        "version": "1.0",
        "action": {
            "name": "submit_decision",
            "surfaceId": "decision",
            "sourceComponentId": "submit",
            "context": {
                "input": "The mug arrived cracked.",
                "instructions": "Did the item arrive damaged?",
                **context,
            },
        },
    }


class FakeDecisionClient:
    def __init__(self, *, answer=None, error=None):
        self.answer = answer or SimpleNamespace(noul=0.99, confidence=0.99)
        self.error = error
        self.calls = []
        self.decisions = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return SimpleNamespace(answers={"decision": self.answer})


def test_surface_route_returns_a2ui_messages():
    response = TestClient(create_app(FakeDecisionClient())).get("/api/surface")

    assert response.status_code == 200
    assert response.json()[0]["version"] == "1.0"
    assert "createSurface" in response.json()[0]


def test_submit_action_returns_a2ui_decision_update():
    fake = FakeDecisionClient()
    response = TestClient(create_app(fake)).post("/api/actions", json=_action())

    assert response.status_code == 200
    assert response.json()[0]["updateDataModel"]["value"] == {
        "label": "Yes",
        "noul": 0.99,
        "confidence": 0.99,
        "noulText": "P(yes) = 0.99",
        "confidenceText": "Confidence = 0.99",
    }
    assert fake.calls[0]["model"] == "gemini-decision-1"


def test_submit_rejects_missing_required_text():
    fake = FakeDecisionClient()
    response = TestClient(create_app(fake)).post(
        "/api/actions", json=_action(input="  ")
    )

    assert response.status_code == 422
    assert fake.calls == []


def test_missing_api_key_returns_503(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = TestClient(create_app()).post("/api/actions", json=_action())

    assert response.status_code == 503
    assert "GEMINI_API_KEY" in response.json()["detail"]


def test_submit_returns_error_without_result_update():
    fake = FakeDecisionClient(error=DecisionUpstreamError("upstream unavailable"))
    response = TestClient(create_app(fake)).post("/api/actions", json=_action())

    assert response.status_code == 502
    assert "updateDataModel" not in response.json()
