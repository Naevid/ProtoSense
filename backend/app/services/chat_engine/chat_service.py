from __future__ import annotations

from typing import Any

from app.models.schemas import AssessmentResponse, ChatResponse, Evidence, ProtocolFeatures
from app.services.extraction_engine.llm_provider import GeminiProvider


class ChatService:
    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    async def answer(
        self,
        protocol_id: str,
        message: str,
        assessment: AssessmentResponse,
        features: ProtocolFeatures,
    ) -> ChatResponse:
        evidence = assessment.evidence
        context = self._context(message, assessment, evidence)
        gemini = await self.provider.answer_assessment_question(context)
        if gemini.get("answer"):
            cited = self._pick_evidence(evidence, gemini.get("cited_features", []))
            return ChatResponse(
                protocol_id=protocol_id,
                answer=str(gemini["answer"]),
                cited_evidence=cited,
                method="gemini",
            )

        answer, cited = self._fallback_answer(message, assessment, evidence)
        return ChatResponse(protocol_id=protocol_id, answer=answer, cited_evidence=cited, method="fallback")

    def _context(self, message: str, assessment: AssessmentResponse, evidence: list[Evidence]) -> dict[str, Any]:
        compact_dimensions = {
            key: {
                "score": value.score,
                "label": value.label,
                "summary": value.summary,
                "top_drivers": [
                    {
                        "feature": driver.feature,
                        "value": driver.value,
                        "contribution_percent": driver.contribution_percent,
                    }
                    for driver in value.top_drivers
                ],
                "recommendations": value.recommendations,
            }
            for key, value in assessment.risk_dimensions.items()
        }
        compact_evidence = [
            {
                "feature": item.feature,
                "snippet": item.snippet,
                "page": item.page,
                "section": item.section,
                "confidence": item.confidence,
                "method": item.method,
            }
            for item in evidence
            if item.snippet
        ][:80]
        return {
            "question": message,
            "overall_feasibility_risk": assessment.overall_feasibility_risk,
            "overall_label": assessment.overall_label,
            "risk_dimensions": compact_dimensions,
            "recommendations": assessment.recommendations,
            "evidence": compact_evidence,
        }

    def _fallback_answer(self, message: str, assessment: AssessmentResponse, evidence: list[Evidence]) -> tuple[str, list[Evidence]]:
        lowered = message.lower()
        dimension_key = self._matched_dimension(lowered)
        if dimension_key and dimension_key in assessment.risk_dimensions:
            dimension = assessment.risk_dimensions[dimension_key]
            cited = [driver.evidence for driver in dimension.top_drivers if driver.evidence][:4]
            drivers = ", ".join(driver.feature.replace("_", " ") for driver in dimension.top_drivers[:3])
            answer = (
                f"{dimension.summary} The main drivers are {drivers}. "
                "The deterministic score comes from the configured feasibility weights, not from the chat assistant."
            )
            if dimension.recommendations:
                answer += " Practical redesign options include " + "; ".join(dimension.recommendations[:2]) + "."
            return answer, cited

        matched = self._keyword_evidence(lowered, evidence)
        if matched:
            features = ", ".join(item.feature.replace("_", " ") for item in matched[:3])
            return (
                f"I found protocol evidence related to {features}. "
                "Use the cited snippets to inspect the source context and decide whether the design choice should be refined.",
                matched[:4],
            )

        top_dimension = max(assessment.risk_dimensions.items(), key=lambda item: item[1].score)
        cited = [driver.evidence for driver in top_dimension[1].top_drivers if driver.evidence][:4]
        return (
            f"The highest current risk area is {top_dimension[0].replace('_', ' ')} at {top_dimension[1].score}. "
            f"{top_dimension[1].summary} Ask about enrollment, site burden, participant burden, startup complexity, amendment susceptibility, or a specific feature for a more targeted answer.",
            cited,
        )

    def _matched_dimension(self, lowered: str) -> str | None:
        aliases = {
            "startup_complexity": ["startup", "activation", "country", "vendor"],
            "enrollment_feasibility": ["enrollment", "eligibility", "patient", "biomarker", "recruit"],
            "participant_burden": ["participant", "visit", "travel", "diary", "burden"],
            "site_execution_burden": ["site", "equipment", "workflow", "training", "pharmacy"],
            "amendment_susceptibility": ["amendment", "ambiguous", "optional", "inconsistency", "interpretation"],
        }
        for key, words in aliases.items():
            if any(word in lowered for word in words):
                return key
        return None

    def _keyword_evidence(self, lowered: str, evidence: list[Evidence]) -> list[Evidence]:
        tokens = {token for token in lowered.replace("?", " ").replace(",", " ").split() if len(token) > 4}
        matches: list[Evidence] = []
        for item in evidence:
            haystack = f"{item.feature} {item.section or ''} {item.snippet}".lower()
            if any(token in haystack for token in tokens):
                matches.append(item)
        return matches

    def _pick_evidence(self, evidence: list[Evidence], cited_features: Any) -> list[Evidence]:
        if not isinstance(cited_features, list):
            return []
        wanted = {str(item) for item in cited_features}
        return [item for item in evidence if item.feature in wanted][:6]
