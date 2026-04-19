# Protocol Feasibility Copilot

Protocol Feasibility Copilot is a hackathon MVP for pre-trial protocol feasibility assessment. It ingests a protocol PDF or text file, extracts structured clinical operations features, maps evidence to page-level snippets, calculates deterministic risk scores, recommends protocol redesign actions, and lets teams simulate assumption changes before launch.

**This is an early feasibility assessment prototype for protocol design support, not a validated predictor of clinical trial outcomes.**

## Product Positioning

The product is intentionally not a generic LLM wrapper. Gemini is used selectively for messy section refinement, semantic extraction, and optional language polishing. The core product value comes from:

- A canonical protocol feature schema
- Deterministic scoring weights
- Evidence-backed traceability
- Recommendation mappings
- A what-if simulation engine
- An enterprise decision-support interface

## Repo Structure

```text
backend/
  app/
    api/                         FastAPI protocol endpoints
    core/                        env config and scoring config
    db/                          SQLite repository
    models/                      Pydantic schemas
    services/
      protocol_ingestion/        upload and PDF/text parsing
      section_mapper/            rule-first section detection
      feature_schema/            feature helpers
      extraction_engine/         deterministic extraction plus Gemini provider
      risk_engine/               deterministic weighted scoring
      explanation_engine/        templated operational summaries
      recommendation_engine/     mapped redesign guidance
      simulation_engine/         assumption overrides and rescoring
      traceability_engine/       evidence collection
frontend/
  app/                           Next.js routes
  components/                    dashboard, evidence, simulator UI
  lib/                           API client and types
samples/                         synthetic protocol fixtures
docs/                            architecture and demo script
```

## Backend Setup

```powershell
cd backend
python -m venv .venv
.\\.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt
cd ..
Copy-Item .env.example .env
uvicorn app.main:app --reload --app-dir backend
```

The backend runs at `http://localhost:8000`.

If `uvicorn` is not on your PATH, start the backend with:

```powershell
.\\scripts\\start-backend.ps1
```

This script uses the local `backend\.vendor` dependency folder when present.

For the cleanest Windows setup, create a project venv first:

```powershell
.\\scripts\\setup-backend.ps1
.\\scripts\\start-backend.ps1
```

Avoid mixing `backend\.vendor` with a different Python version. If you see a `pydantic_core` import error, your terminal is using a different Python version than the one used to install `backend\.vendor`; the venv setup above fixes that.

Gemini is optional for local demo flow. If `GEMINI_API_KEY` is unset, the app falls back to deterministic extraction and inferred labels. The default Gemini model is `models/gemini-2.5-flash`.

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:3000`.

Or from the repo root:

```powershell
.\\scripts\\start-frontend.ps1
```

## API

- `POST /protocols/upload`
- `POST /protocols/{id}/section-map`
- `POST /protocols/{id}/extract`
- `POST /protocols/{id}/score`
- `GET /protocols/{id}/assessment`
- `POST /protocols/{id}/simulate`
- `GET /protocols/{id}/recommendations`
- `GET /protocols/{id}/evidence`

## Demo Flow

1. Start the backend and frontend.
2. Open `http://localhost:3000`.
3. Upload `samples/synthetic_oncology_protocol.txt`.
4. Review overall feasibility risk and the five risk dimensions.
5. Open the evidence drawer to inspect snippets, confidence, pages, and extraction source.
6. Use the simulator to reduce exploratory endpoints, lower in-person visits, or toggle specialized equipment and observe score deltas.

## Scoring Model

Risk scoring is deterministic after feature extraction. The weights live in `backend/app/core/scoring_config.py` and cover:

- Startup Complexity Risk
- Enrollment Feasibility Risk
- Participant Burden Risk
- Site Execution Burden Risk
- Amendment Susceptibility Risk
- Overall Feasibility Risk

Each dimension returns a 0-100 score, Low/Medium/High label, top drivers, driver contribution percentages, summaries, evidence, and recommendations.

## Gemini Usage

Gemini sits behind `GeminiProvider` in `backend/app/services/extraction_engine/llm_provider.py`. It can refine section maps and fill hard semantic features, but it does not generate risk scores. Responses are cached under `backend/data/cache` for identical prompts.
