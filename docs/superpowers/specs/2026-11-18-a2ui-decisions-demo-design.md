# A2UI Decisions Demo Design

## Intent

Turn the existing Gemini Decision 1 Python example into a small local app where
a user can enter text and a yes/no question, optionally define what yes and no
mean, and receive a decision result in an A2UI-rendered interface.

## Goals

- Use the A2UI v1.0 protocol for the form and result surface.
- Call `gemini-decision-1` through the Python Google Gen AI SDK.
- Show the yes probability, confidence, and a readable yes/no result. For the
  readable result, use `noul >= 0.5` as yes.
- Keep the Gemini API key on the server and read it from `GEMINI_API_KEY`.
- Show loading and API/validation errors explicitly; never present an error as a
  successful decision.
- Clear a previous result when a new decision is submitted so an error cannot
  be mistaken for an earlier successful result.

## Non-goals

- Dynamically generating UI with a second generative model or agent runtime.
- Supporting choice/score questions, authentication, deployment, or persistent
  decision history.
- Treating the probability or confidence as a guarantee of correctness.

## Constraints

- The repository currently has only `README.md` and `demo.py`; there is no
  existing web framework, frontend, or test setup.
- The browser must not receive the Gemini API key.
- Use the official A2UI React renderer and a server-side A2UI-compatible
  implementation; do not invent a parallel UI message format.
- Keep the existing command-line demo working.

## Approaches

1. **Fixed A2UI surface (selected):** Python serves the app and calls Decisions
   API; a React client renders a fixed form and result surface using the official
   A2UI renderer. This keeps UI and decision responsibilities separate without
   introducing another model.
2. **Generative A2UI agent:** an agent runtime generates surfaces dynamically.
   This is more adaptable, but adds an unnecessary model/runtime for a fixed
   yes/no decision flow.
3. **Ordinary web form:** simplest implementation, but it does not meet the
   requirement to use the A2UI protocol and renderer.

## Proposed flow

1. The server sends an A2UI surface containing fields for shared input,
   decision instructions, optional true/false descriptions, and a submit
   action.
2. The client sends the A2UI action and current bound form data to the server.
3. The server validates required fields, calls
   `client.decisions.create(model="gemini-decision-1", ...)`, and returns an
   A2UI data-model update for the result on the same surface.
4. The surface displays Yes or No (`noul >= 0.5`), `noul`, and `confidence`.
   Failures are returned as explicit errors and displayed without a result.

## Implementation choices left to the builder

- Use a small Python HTTP application (FastAPI) to serve the client and accept
  A2UI actions, preserving the existing Python SDK usage.
- Use a React/TypeScript client with Vite and the official A2UI React package.
- Use official A2UI v1.0 messages for surface creation, actions, and result
  updates. Keep the form surface fixed and data-bound.
- Add focused tests for request mapping, omitted optional criteria, result
  interpretation, and error handling. Mock the external Decisions API call so
  tests require no credentials or network access.
