from __future__ import annotations

from typing import Literal, Mapping, Protocol

from google.genai import errors
from pydantic import BaseModel, Field, field_validator


class DecisionInput(BaseModel):
    input: str = Field(min_length=1)
    instructions: str = Field(min_length=1)
    true_description: str | None = None
    false_description: str | None = None

    @field_validator("input", "instructions")
    @classmethod
    def require_nonblank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("true_description", "false_description")
    @classmethod
    def normalize_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class DecisionResult(BaseModel):
    noul: float
    confidence: float
    label: Literal["Yes", "No"]


class _DecisionsResource(Protocol):
    def create(
        self,
        *,
        model: str,
        input: str,
        questions: Mapping[str, object],
    ) -> object: ...


class DecisionClient(Protocol):
    decisions: _DecisionsResource


class DecisionResponseError(RuntimeError):
    pass


class DecisionUpstreamError(RuntimeError):
    pass


def evaluate_decision(
    data: DecisionInput, client: DecisionClient
) -> DecisionResult:
    question: dict[str, object] = {
        "type": "noul",
        "instructions": data.instructions,
    }
    criteria = {
        key: value
        for key, value in (
            ("true_description", data.true_description),
            ("false_description", data.false_description),
        )
        if value is not None
    }
    if criteria:
        question["criteria"] = criteria

    try:
        response = client.decisions.create(
            model="gemini-decision-1",
            input=data.input,
            questions={"decision": question},
        )
    except errors.APIError as exc:
        raise DecisionUpstreamError("Gemini Decisions API request failed") from exc

    answers = getattr(response, "answers", None)
    answer = answers.get("decision") if answers else None
    if answer is None:
        raise DecisionResponseError(
            "Gemini Decisions API response is missing the decision answer"
        )

    noul = float(answer.noul)
    confidence = float(answer.confidence)
    return DecisionResult(
        noul=noul,
        confidence=confidence,
        label="Yes" if noul >= 0.5 else "No",
    )
