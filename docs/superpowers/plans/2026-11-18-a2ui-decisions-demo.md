# A2UI Decisions Demo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local A2UI v1.0 web app that sends a user-defined yes/no question to Gemini Decision 1 and displays its result.

**Architecture:** A Python FastAPI service validates A2UI submit actions and calls the Google Gen AI Python SDK. A React client uses the official A2UI renderer and Basic Catalog for the bound form and result surface; the service returns protocol messages, not custom UI data.

**Tech Stack:** Python 3.10+, FastAPI, google-genai, A2UI v1.0 JSON messages, React, TypeScript, Vite, `@a2ui/react`, `@a2ui/web_core`, pytest, Vitest.

**Spec:** `docs/superpowers/specs/2026-11-18-a2ui-decisions-demo-design.md`

## Global Constraints

- The Gemini key is read from `GEMINI_API_KEY` on the server and is never sent to the browser.
- The decision model is `gemini-decision-1`; API version is `v1beta`.
- A readable result is Yes when `noul >= 0.5`, otherwise No; always show `noul` and `confidence`.
- The existing `demo.py` CLI example remains usable.
- The UI uses A2UI v1.0 messages and official React renderer/Basic Catalog components.

## Review Focus

- Empty or whitespace-only input/instructions must return a validation error and make no Decisions API call; test in `test_submit_rejects_missing_required_text`.
- Empty criteria descriptions must be omitted rather than sent as meaningful criteria; test in `test_evaluate_omits_blank_criteria`.
- A response without the requested answer must surface an explicit server error, not a decision; test in `test_submit_rejects_missing_answer`.
- Probabilities on either side of 0.5 must produce the correct readable result while preserving calibrated values; test in `test_evaluate_returns_probability_confidence_and_label`.
- API failures must be shown as errors without stale or fabricated decision values; test in `test_submit_returns_error_without_result_update`.

---

### Task 1: Implement the Python Decisions API and A2UI action endpoint

**Files:**
- Create: `pyproject.toml`
- Create: `app/__init__.py`
- Create: `app/decisions.py`
- Create: `app/a2ui.py`
- Create: `app/main.py`
- Create: `tests/test_decisions.py`
- Create: `tests/test_a2ui.py`
- Create: `tests/test_api.py`

**Interfaces:**
- `DecisionInput`: `input`, `instructions`, and optional `true_description` / `false_description` strings.
- `DecisionResult`: `noul: float`, `confidence: float`, `label: Literal["Yes", "No"]`.
- `DecisionClient`: a protocol exposing `decisions.create(*, model: str, input: str, questions: Mapping[str, object])`.
- `evaluate_decision(data: DecisionInput, client: DecisionClient) -> DecisionResult`: issues one `client.decisions.create` call and rejects a missing answer.
- `initial_surface() -> list[dict[str, object]]`: returns A2UI v1.0 create-surface messages using the Basic Catalog.
- `decision_update(result: DecisionResult) -> list[dict[str, object]]`: returns an A2UI v1.0 data-model update for `/result`.
- `create_app(decision_client: DecisionClient | None = None) -> FastAPI`: exposes `GET /api/surface` and `POST /api/actions`; constructs the Google client only when no test client is injected.
- `POST /api/actions` accepts a v1.0 `submit_decision` action with resolved form values in `action.context`, and returns an A2UI update message. Invalid input is HTTP 422; unavailable API credentials are HTTP 503; upstream failures are HTTP 502.

- [ ] **Step 1: Write failing tests** in `tests/test_decisions.py`, `tests/test_a2ui.py`, and `tests/test_api.py`:
  - `test_evaluate_omits_blank_criteria`: assert the SDK receives no `criteria` when both descriptions are blank.
  - `test_evaluate_returns_probability_confidence_and_label`: for `noul` values `0.03` and `0.99`, assert No/Yes respectively and preserve the returned probabilities.
  - `test_submit_rejects_missing_answer`: assert a missing `decision` answer raises an explicit service error.
  - `test_initial_surface_uses_a2ui_v1`: assert `version == "1.0"`, the Basic Catalog ID, bound input fields, and a `submit_decision` action.
  - `test_submit_rejects_missing_required_text`: assert HTTP 422 and no SDK call for blank input or instructions.
  - `test_missing_api_key_returns_503`: assert missing server credentials produce an explicit error and no decision update.
  - `test_submit_returns_error_without_result_update`: assert an upstream failure returns HTTP 502, not an A2UI success update.
- [ ] **Step 2: Run `pytest -q`** and confirm failures are caused by the absent app behavior.
- [ ] **Step 3: Implement typed request/result handling, A2UI v1.0 message construction, and the two FastAPI routes.** Inject the Decisions client for tests; read `GEMINI_API_KEY` only when constructing the production client.
- [ ] **Step 4: Run `pytest -q`** and confirm all backend tests pass without network credentials.

### Task 2: Build the React A2UI client

**Files:**
- Create: `web/package.json`
- Create: `web/tsconfig.json`
- Create: `web/vite.config.ts`
- Create: `web/index.html`
- Create: `web/src/main.tsx`
- Create: `web/src/App.tsx`
- Create: `web/src/decisionClient.ts`
- Create: `web/src/App.test.tsx`
- Create: `web/src/styles.css`

**Interfaces:**
- `App` loads messages from `GET /api/surface`, processes them with `MessageProcessor([basicCatalog])`, and renders its surface with `A2uiSurface`.
- `submitDecisionAction(processor, action, fetcher)` posts A2UI actions to `/api/actions` and applies returned A2UI messages through the same processor.
- A new submission clears any prior result and sets loading state. Transport errors are converted into local A2UI `/error` data-model updates, leaving no stale result visible.

- [ ] **Step 1: Write a failing `test_submit_applies_a2ui_result_update`** that feeds a `submit_decision` action through the app transport and asserts the official `MessageProcessor` applies the returned `/result` update to the rendered surface. Also assert failure clears old result data and renders the error.
- [ ] **Step 2: Run `cd web && npm test -- --run`** and confirm the test fails because the app/transport behavior is missing.
- [ ] **Step 3: Implement the A2UI client** using the official React renderer, v1.0 Basic Catalog, and Vite proxy to the Python service.
- [ ] **Step 4: Run `cd web && npm test -- --run && npm run build`** and confirm both pass.

### Task 3: Document setup and verify the full local demo

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update the README** with Python and Node setup, `GEMINI_API_KEY`, two-terminal development commands, the UI workflow, and the existing CLI demo.
- [ ] **Step 2: Run the full Python and frontend test/build commands** from Tasks 1 and 2.
- [ ] **Step 3: Verify the app starts locally** with the documented commands and the browser UI receives the initial A2UI surface. A real decision request requires a user-provided API key and is not part of automated tests.
