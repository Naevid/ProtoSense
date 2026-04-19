from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from app.core.config import get_settings
from app.models.schemas import ProtocolPage, ProtocolSection

logger = logging.getLogger(__name__)


class GeminiProvider:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.cache_dir = self.settings.cache_dir

    async def refine_sections(
        self, pages: list[ProtocolPage], sections: list[ProtocolSection]
    ) -> list[ProtocolSection] | None:
        prompt = {
            "task": "Refine a clinical trial protocol section map.",
            "expected_sections": [
                "study summary",
                "objectives",
                "endpoints",
                "study design",
                "inclusion criteria",
                "exclusion criteria",
                "schedule of assessments",
                "procedures",
                "safety",
                "site requirements",
                "operational notes",
            ],
            "current_sections": [section.model_dump() for section in sections],
            "page_previews": [{"page": p.page, "text": p.text[:1800]} for p in pages[:20]],
            "return_json": "array of {name,start_page,end_page,heading,confidence,method}",
        }
        data = await self._generate_json("section_refinement", prompt)
        if not isinstance(data, list):
            return None
        try:
            return [ProtocolSection(**{**item, "method": "gemini"}) for item in data]
        except Exception as exc:
            logger.warning("Gemini section refinement returned invalid data: %s", exc)
            return None

    async def semantic_feature_fill(self, context: dict[str, Any]) -> dict[str, Any]:
        prompt = {
            "task": "Extract only hard-to-parse protocol feasibility features as strict JSON.",
            "rules": [
                "Do not score risk.",
                "Return values, confidence, supporting snippet, page, and section.",
                "Use null when unsupported by evidence.",
            ],
            "schema_fields": [
                "endpoint_novelty_level",
                "eligibility_restrictiveness_level",
                "procedure_intensity_level",
                "participant_burden_level",
                "central_lab_complexity",
                "imaging_complexity",
                "pharmacy_handling_complexity",
                "workflow_fragmentation_level",
                "site_burden_level",
                "safety_reporting_complexity",
                "oversight_complexity_level",
                "operational_complexity_level",
                "ambiguous_operational_language_flag",
                "internal_inconsistency_flag",
                "excessive_optional_content_flag",
                "likely_site_interpretation_variance_flag",
            ],
            "context": context,
        }
        data = await self._generate_json("semantic_feature_fill", prompt)
        return data if isinstance(data, dict) else {}

    async def polish_explanations(self, payload: dict[str, Any]) -> dict[str, str]:
        prompt = {
            "task": "Polish operational feasibility summaries. Preserve facts and avoid predictive claims.",
            "payload": payload,
            "return_json": "object mapping risk dimension keys to concise summaries",
        }
        data = await self._generate_json("polish_explanations", prompt)
        return data if isinstance(data, dict) else {}

    async def answer_assessment_question(self, payload: dict[str, Any]) -> dict[str, Any]:
        prompt = {
            "task": "Answer a user question about a clinical protocol feasibility assessment.",
            "rules": [
                "Use only the supplied assessment, extracted features, recommendations, and evidence snippets.",
                "Do not generate new risk scores.",
                "Do not claim validated prediction of clinical trial outcomes.",
                "Cite evidence by feature name when making protocol-specific claims.",
                "If the supplied context is insufficient, say what is missing.",
                "Keep the answer concise and operationally useful."
            ],
            "payload": payload,
            "return_json": {
                "answer": "string",
                "cited_features": ["feature_name"]
            },
        }
        data = await self._generate_json("assessment_chat", prompt)
        return data if isinstance(data, dict) else {}

    async def _generate_json(self, namespace: str, prompt: dict[str, Any]) -> Any:
        cache_key = hashlib.sha256(json.dumps(prompt, sort_keys=True).encode("utf-8")).hexdigest()
        cache_file = Path(self.cache_dir) / f"{namespace}_{cache_key}.json"
        if cache_file.exists():
            return json.loads(cache_file.read_text(encoding="utf-8"))

        if not self.settings.enable_gemini or not self.settings.gemini_api_key:
            logger.info(
                "Gemini skipped for %s because ENABLE_GEMINI=%s and key configured=%s",
                namespace,
                self.settings.enable_gemini,
                bool(self.settings.gemini_api_key),
            )
            return None

        try:
            import google.generativeai as genai

            genai.configure(api_key=self.settings.gemini_api_key)
            model = genai.GenerativeModel(self.settings.gemini_model)
            response = model.generate_content(
                "Return valid JSON only.\n" + json.dumps(prompt),
                generation_config={"response_mime_type": "application/json"},
            )
            data = json.loads(response.text)
            cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            return data
        except Exception as exc:
            logger.warning("Gemini request failed for %s: %s", namespace, exc)
            return None
