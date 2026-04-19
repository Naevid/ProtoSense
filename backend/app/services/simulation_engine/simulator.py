from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.core.scoring_config import SIMULATOR_FIELDS
from app.models.schemas import AssessmentResponse, FeatureValue, ProtocolFeatures, SimulationResponse
from app.services.feature_schema.utils import find_feature, set_feature
from app.services.risk_engine.scorer import RiskScorer


class SimulationEngine:
    def __init__(self) -> None:
        self.scorer = RiskScorer()

    def simulate(self, protocol_id: str, features: ProtocolFeatures, overrides: dict[str, Any]) -> SimulationResponse:
        invalid = sorted(set(overrides) - SIMULATOR_FIELDS)
        if invalid:
            raise ValueError(f"Unsupported simulator fields: {', '.join(invalid)}")

        before = self.scorer.build_assessment(protocol_id, features)
        simulated = deepcopy(features)
        applied: dict[str, Any] = {}
        for feature_name, value in overrides.items():
            existing = find_feature(simulated, feature_name)
            replacement = FeatureValue(
                value=value,
                confidence=existing.confidence if existing else 1.0,
                method="user_simulation",
                supporting_snippet=f"Simulator override for {feature_name}: {value}",
                page=existing.page if existing else None,
                section=existing.section if existing else "simulation",
            )
            if set_feature(simulated, feature_name, replacement):
                applied[feature_name] = value

        after = self.scorer.build_assessment(protocol_id, simulated)
        deltas = {"overall_feasibility_risk": after.overall_feasibility_risk - before.overall_feasibility_risk}
        for key, after_dimension in after.risk_dimensions.items():
            deltas[key] = after_dimension.score - before.risk_dimensions[key].score
        return SimulationResponse(protocol_id=protocol_id, before=before, after=after, deltas=deltas, applied_overrides=applied)
