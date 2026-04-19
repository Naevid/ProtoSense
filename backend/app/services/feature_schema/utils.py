from __future__ import annotations

from typing import Any

from app.models.schemas import FeatureValue, ProtocolFeatures


def make_feature(value: Any, confidence: float, method: str, snippet: str, page: int | None, section: str | None) -> FeatureValue:
    return FeatureValue(
        value=value,
        confidence=confidence,
        method=method,  # type: ignore[arg-type]
        supporting_snippet=(snippet or "")[:700],
        page=page,
        section=section,
    )


def iter_feature_values(features: ProtocolFeatures):
    for group_name, group in features:
        for feature_name, feature_value in group:
            yield group_name, feature_name, feature_value


def find_feature(features: ProtocolFeatures, feature_name: str) -> FeatureValue | None:
    for _, candidate_name, value in iter_feature_values(features):
        if candidate_name == feature_name:
            return value
    return None


def set_feature(features: ProtocolFeatures, feature_name: str, value: FeatureValue) -> bool:
    for _, group in features:
        if hasattr(group, feature_name):
            setattr(group, feature_name, value)
            return True
    return False
