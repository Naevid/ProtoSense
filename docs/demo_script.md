# Demo Script

## Opening

Protocol Feasibility Copilot helps clinical operations and protocol design teams identify operational friction before trial launch. It does not predict exact delays. It turns protocol text into structured feasibility features, evidence-backed risk drivers, and redesign guidance.

## Flow

1. Open the landing page.
2. Navigate to upload.
3. Upload `samples/synthetic_oncology_protocol.txt`.
4. Explain that the backend preserves page-level source text and builds a section map before extraction.
5. Show the dashboard:
   - Overall Feasibility Risk
   - Startup Complexity Risk
   - Enrollment Feasibility Risk
   - Participant Burden Risk
   - Site Execution Burden Risk
   - Amendment Susceptibility Risk
6. Open the evidence drawer:
   - Point out page, section, confidence, extraction source, and snippet.
   - Explain that Gemini can help with semantic judgments, but the deterministic risk model owns scoring.
7. Show recommendations:
   - Rationalize eligibility criteria
   - Reduce exploratory endpoints
   - Consolidate visits
   - Pre-qualify specialized sites
8. Use the simulator:
   - Reduce exploratory endpoints from 6 to 2.
   - Reduce in-person visits from 14 to 9.
   - Toggle specialized equipment off.
   - Run simulation and show before/after deltas.

## Closing

The differentiator is traceable protocol intelligence: schema, scoring, evidence, recommendations, and simulation. Gemini is one layer inside the product, not the product itself.
