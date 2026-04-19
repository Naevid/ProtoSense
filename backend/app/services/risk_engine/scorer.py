from __future__ import annotations

from typing import Any

from app.core.scoring_config import OVERALL_WEIGHTS, RISK_WEIGHTS
from app.models.schemas import AssessmentResponse, ProtocolFeatures, RiskDimension, TopDriver
from app.services.explanation_engine.explainer import ExplanationEngine
from app.services.feature_schema.utils import find_feature, iter_feature_values
from app.services.recommendation_engine.recommender import RecommendationEngine
from app.services.traceability_engine.traceability import TraceabilityEngine


LEVEL_VALUES = {"low": 20, "medium": 55, "high": 90}


class RiskScorer:
    def __init__(self) -> None:
        self.traceability = TraceabilityEngine()
        self.explainer = ExplanationEngine()
        self.recommender = RecommendationEngine()

    def build_assessment(self, protocol_id: str, features: ProtocolFeatures) -> AssessmentResponse:
        dimensions: dict[str, RiskDimension] = {}
        all_driver_names: list[str] = []
        for dimension, weights in RISK_WEIGHTS.items():
            scored = self._score_dimension(features, weights)
            all_driver_names.extend([driver.feature for driver in scored["drivers"]])
            driver_names = [driver.feature for driver in scored["drivers"][:3]]
            dimensions[dimension] = RiskDimension(
                score=scored["score"],
                label=self._label(scored["score"]),
                top_drivers=scored["drivers"][:5],
                summary=self.explainer.summarize(dimension, scored["score"], driver_names),
                recommendations=self.recommender.recommendation_texts_for_dimension(driver_names),
            )

        overall = round(sum(dimensions[name].score * weight for name, weight in OVERALL_WEIGHTS.items()))
        recs = self.recommender.generate(features, all_driver_names)
        return AssessmentResponse(
            protocol_id=protocol_id,
            overall_feasibility_risk=overall,
            overall_label=self._label(overall),
            risk_dimensions=dimensions,
            features=features.model_dump(),
            evidence=self.traceability.collect_evidence(features),
            recommendations=recs,
        )

    def _score_dimension(self, features: ProtocolFeatures, weights: dict[str, float]) -> dict[str, Any]:
        raw_contributions: list[tuple[str, float, Any]] = []
        positive_capacity = sum(abs(w) for w in weights.values() if w > 0)
        raw_score = 0.0
        for feature_name, weight in weights.items():
            feature = find_feature(features, feature_name)
            normalized = self._normalize_feature(feature_name, feature.value if feature else None)
            contribution = normalized * weight
            raw_score += contribution
            if contribution > 0:
                raw_contributions.append((feature_name, contribution, feature.value if feature else None))

        score = max(0, min(100, round(raw_score / max(1.0, positive_capacity))))
        total_positive = sum(item[1] for item in raw_contributions) or 1
        drivers = [
            TopDriver(
                feature=name,
                impact=round(impact / max(1.0, positive_capacity), 1),
                contribution_percent=round((impact / total_positive) * 100, 1),
                value=value,
                evidence=self.traceability.evidence_for(features, name),
            )
            for name, impact, value in sorted(raw_contributions, key=lambda item: item[1], reverse=True)
        ]
        return {"score": score, "drivers": drivers}

    def _normalize_feature(self, feature_name: str, value: Any) -> float:
        if value is None or value == "":
            return 0
        if isinstance(value, bool):
            return 100 if value else 0
        if isinstance(value, str):
            lowered = value.lower().strip()
            if lowered in LEVEL_VALUES:
                return LEVEL_VALUES[lowered]
            if lowered in {"yes", "true", "present"}:
                return 100
            if lowered in {"no", "false", "absent"}:
                return 0
            return 35
        try:
            number = float(value)
        except (TypeError, ValueError):
            return 0

        caps = {
            "number_of_countries": 12,
            "number_of_sites": 80,
            "target_sample_size": 800,
            "exclusion_count": 18,
            "inclusion_count": 14,
            "total_visit_count": 16,
            "in_person_visit_count": 14,
            "remote_visit_count": 10,
            "invasive_procedures_count": 5,
            "number_of_timepoints": 18,
            "number_of_assessment_types": 10,
            "number_exploratory_endpoints": 8,
            "number_secondary_endpoints": 12,
            "number_primary_endpoints": 4,
        }
        cap = caps.get(feature_name, 10)
        return max(0, min(100, (number / cap) * 100))

    def _label(self, score: int) -> str:
        if score >= 67:
            return "High"
        if score >= 34:
            return "Medium"
        return "Low"
