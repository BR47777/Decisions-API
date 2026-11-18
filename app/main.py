from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI, HTTPException
from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict

from app.a2ui import decision_update, initial_surface
from app.decisions import (
    DecisionClient,
    DecisionInput,
    DecisionResponseError,
    DecisionUpstreamError,
    evaluate_decision,
)

logger = logging.getLogger(__name__)


class A2UIAction(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: Literal["submit_decision"]
    context: DecisionInput


class A2UIActionMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    version: Literal["1.0"]
    action: A2UIAction


def create_app(decision_client: DecisionClient | None = None) -> FastAPI:
    owned_clients: list[genai.Client] = []
    production_client: genai.Client | None = None

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        yield
        for client in owned_clients:
            client.close()

    app = FastAPI(title="A2UI Decisions Demo", lifespan=lifespan)

    @app.get("/api/surface")
    def get_surface() -> list[dict[str, object]]:
        return initial_surface()

    @app.post("/api/actions")
    def submit_action(message: A2UIActionMessage) -> list[dict[str, object]]:
        nonlocal production_client
        client = decision_client
        if client is None:
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise HTTPException(
                    status_code=503,
                    detail="Set GEMINI_API_KEY on the server to enable decisions.",
                )
            if production_client is None:
                production_client = genai.Client(
                    api_key=api_key,
                    http_options=types.HttpOptions(api_version="v1beta"),
                )
                owned_clients.append(production_client)
            client = production_client

        try:
            result = evaluate_decision(message.action.context, client)
        except DecisionResponseError as exc:
            logger.error("%s", exc)
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except DecisionUpstreamError as exc:
            logger.exception("Gemini Decisions API request failed")
            raise HTTPException(
                status_code=502,
                detail="Gemini Decisions API request failed. Please try again.",
            ) from exc
        return decision_update(result)

    return app


app = create_app()
