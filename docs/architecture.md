# Architecture and Implementation Checklist

## 1. Folder Structure

The repo is split into `backend`, `frontend`, `samples`, and `docs`. Backend modules mirror the product architecture: ingestion, section mapping, feature extraction, scoring, explanations, recommendations, simulation, and traceability. Frontend modules mirror the user workflow: landing, upload, results dashboard, simulator, and evidence drawer.

## 2. Core Backend Schemas

`backend/app/models/schemas.py` defines:

- `FeatureValue`: value, confidence, extraction method, snippet, page, section
- `Evidence`: inspectable traceability record
- `ProtocolFeatures`: canonical nested feature schema
- `ProtocolSection`: section map entry
- `RiskDimension`: score, label, top drivers, summary, recommendations
- `AssessmentResponse`: full assessment payload
- `SimulationRequest` and `SimulationResponse`

## 3. Scoring Config

`backend/app/core/scoring_config.py` stores editable scoring weights. The score engine normalizes extracted feature values, applies the dimension weights, calculates contribution percentages, and returns transparent driver attribution.

## 4. Extraction Pipeline Design

Pipeline order:

1. PDF or text ingestion with page preservation
2. Deterministic heading detection for protocol section mapping
3. Gemini section refinement only if rule coverage is sparse
4. Rule-based extraction for counts, flags, endpoints, visits, eligibility, equipment, vendors, and safety terms
5. Gemini semantic fill for nuanced burden, restrictiveness, novelty, fragmentation, ambiguity, and inconsistency
6. Pydantic validation and graceful fallback to inferred values
7. Evidence collection for each important feature

## 5. API Routes

Implemented routes:

- `POST /protocols/upload`
- `POST /protocols/{id}/section-map`
- `POST /protocols/{id}/extract`
- `POST /protocols/{id}/score`
- `GET /protocols/{id}/assessment`
- `POST /protocols/{id}/simulate`
- `GET /protocols/{id}/recommendations`
- `GET /protocols/{id}/evidence`

## 6. Frontend Component Plan

- Landing page: product positioning and protocol feasibility framework
- Upload page: file intake and pipeline progress
- Dashboard page: overall score, five dimension cards, driver bars, recommendations
- Evidence drawer: snippets with page, section, confidence, and extraction method
- Simulator: sliders and toggles for editable assumptions with before/after deltas

## 7. Implementation Checklist

- [x] Scaffold backend and frontend folders
- [x] Define Pydantic schemas for canonical protocol features
- [x] Implement PDF/text upload and page-preserving parsing
- [x] Implement rule-first section mapping
- [x] Add Gemini provider abstraction and response cache
- [x] Implement deterministic extraction heuristics
- [x] Implement semantic extraction hook and fallback
- [x] Implement weighted risk engine and driver attribution
- [x] Implement recommendation mapping logic
- [x] Implement simulator overrides and rescoring
- [x] Implement traceability evidence collection
- [x] Implement FastAPI routes
- [x] Implement Next.js landing, upload, dashboard, evidence, and simulator views
- [x] Add synthetic samples
- [x] Add README and demo script
- [ ] Add automated backend unit tests
- [ ] Add browser screenshot verification
- [ ] Add richer schedule-of-assessments table parsing
