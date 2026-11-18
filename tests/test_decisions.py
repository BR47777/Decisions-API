from types import SimpleNamespace

import pytest

from app.decisions import (
    DecisionInput,
    DecisionResponseError,
    evaluate_decision,
)


class FakeDecisionClient:
    def __init__(self, answer):
        self.answer = answer
        self.calls = []
        self.decisions = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            answers={} if self.answer is None else {"decision": self.answer}
        )


def test_evaluate_omits_blank_criteria():
    client = FakeDecisionClient(SimpleNamespace(noul=0.03, confidence=0.97))

    result = evaluate_decision(
        DecisionInput(
            input="Returned because the color was not preferred.",
            instructions="Is this a defect?",
            true_description=" ",
            false_description="",
        ),
        client,
    )

    assert result.label == "No"
    assert client.calls[0]["questions"] == {
        "decision": {
            "type": "noul",
            "instructions": "Is this a defect?",
        }
    }


def test_evaluate_includes_nonblank_criteria():
    client = FakeDecisionClient(SimpleNamespace(noul=0.99, confidence=0.99))

    evaluate_decision(
        DecisionInput(
            input="The item arrived broken.",
            instructions="Is this a defect?",
            true_description="The item is broken.",
            false_description="The item works as expected.",
        ),
        client,
    )

    assert client.calls[0]["questions"]["decision"]["criteria"] == {
        "true_description": "The item is broken.",
        "false_description": "The item works as expected.",
    }


@pytest.mark.parametrize(
    ("noul", "label"),
    [(0.03, "No"), (0.5, "Yes"), (0.99, "Yes")],
)
def test_evaluate_returns_probability_confidence_and_label(noul, label):
    client = FakeDecisionClient(SimpleNamespace(noul=noul, confidence=0.97))

    result = evaluate_decision(
        DecisionInput(input="Item is cracked.", instructions="Is it damaged?"),
        client,
    )

    assert result.label == label
    assert result.noul == noul
    assert result.confidence == 0.97


def test_submit_rejects_missing_answer():
    client = FakeDecisionClient(None)

    with pytest.raises(DecisionResponseError, match="missing the decision answer"):
        evaluate_decision(
            DecisionInput(input="Item is cracked.", instructions="Is it damaged?"),
            client,
        )
