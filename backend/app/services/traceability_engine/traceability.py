from __future__ import annotations

from app.models.schemas import Evidence, ProtocolFeatures
from app.services.feature_schema.utils import iter_feature_values


class TraceabilityEngine:
    def collect_evidence(self, features: ProtocolFeatures) -> list[Evidence]:
        evidence: list[Evidence] = []
        for _, feature_name, feature_value in iter_feature_values(features):
            if feature_value.supporting_snippet or feature_value.page or feature_value.method:
                evidence.append(feature_value.evidence(feature_name))
        return evidence

    def evidence_for(self, features: ProtocolFeatures, feature_name: str) -> Evidence | None:
        for _, candidate_name, feature_value in iter_feature_values(features):
            if candidate_name == feature_name:
                return feature_value.evidence(feature_name)
        return None
