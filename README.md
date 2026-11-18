# Decisions API demo

A local A2UI v1.0 web app for asking Gemini Decision 1 a yes/no question about
text. The Python server keeps the Gemini API key private; the React client uses
the official A2UI renderer to show the form and calibrated result.

## Requirements

- Python 3.10+
- Node.js and npm
- A Gemini API key with access to `gemini-decision-1`

## Run the web app

Install the Python dependencies and set the API key:

```bash
python -m pip install -e ".[dev]"
export GEMINI_API_KEY="your-api-key"
```

Start the API server in one terminal:

```bash
uvicorn app.main:app --reload
```

Start the A2UI client in another terminal:

```bash
cd web
npm install
npm run dev
```

Open the local URL printed by Vite. Enter the text to evaluate and a focused
yes/no question. The optional true/false descriptions let you define how each
outcome should be interpreted. The result shows Yes or No (`noul >= 0.5`),
`P(yes)`, and confidence. Confidence and probability are signals, not guarantees;
choose thresholds appropriate to your application.

## Tests and build

```bash
pytest -q
cd web
npm test -- --run
npm run build
```

## Command-line example

The original SDK example is available in [`demo.py`](./demo.py):

```bash
python demo.py
```
