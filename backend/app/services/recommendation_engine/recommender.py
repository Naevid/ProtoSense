from __future__ import annotations

from typing import Any

from app.models.schemas import Evidence, ProtocolFeatures
from app.services.feature_schema.utils import find_feature
from app.services.traceability_engine.traceability import TraceabilityEngine


RECOMMENDATION_MAP: dict[str, dict[str, str]] = {
    "eligibility_restrictiveness_level": {
        "title": "Rationalize eligibility criteria",
        "action": "Review inclusion and exclusion criteria for operational necessity, especially criteria that narrow the reachable patient pool without changing safety or endpoint integrity.",
        "impact_area": "Enrollment feasibility",
    },
    "biomarker_requirement": {
        "title": "Pre-qualify biomarker-ready sites",
        "action": "Assess patient pool, tissue availability, assay turnaround time, and site testing workflows before activation.",
        "impact_area": "Enrollment feasibility",
    },
    "number_exploratory_endpoints": {
        "title": "Prune low-value exploratory endpoints",
        "action": "Separate must-have endpoints from exploratory nice-to-haves and remove assessments unlikely to inform go/no-go decisions.",
        "impact_area": "Amendment susceptibility",
    },
    "total_visit_count": {
        "title": "Consolidate visit schedule",
        "action": "Combine compatible assessments into fewer visits and convert suitable follow-ups to remote capture.",
        "impact_area": "Participant burden",
    },
    "in_person_visit_count": {
        "title": "Shift feasible visits away from site-only execution",
        "action": "Evaluate remote or local-lab options for lower-risk assessments to reduce participant travel and site congestion.",
        "impact_area": "Participant burden",
    },
    "specialized_equipment_required": {
        "title": "Screen site capability earlier",
        "action": "Flag equipment-dependent procedures during feasibility outreach and create a site capability checklist before selection.",
        "impact_area": "Site execution burden",
    },
    "multiple_vendor_dependencies": {
        "title": "Reduce vendor handoffs",
        "action": "Clarify ownership across vendors, central labs, imaging, devices, and EDC workflows before first site initiation.",
        "impact_area": "Startup complexity",
    },
    "workflow_fragmentation_level": {
        "title": "Simplify site workflow choreography",
        "action": "Collapse fragmented procedures into a smaller number of site workflows with clear sequencing and escalation paths.",
        "impact_area": "Site execution burden",
    },
    "ambiguous_operational_language_flag": {
        "title": "Replace discretionary operational wording",
        "action": "Convert phrases such as 'as appropriate' or 'where feasible' into explicit decision rules to reduce site interpretation variance.",
        "impact_area": "Amendment susceptibility",
    },
    "endpoint_novelty_level": {
        "title": "De-risk endpoint execution",
        "action": "Create endpoint-specific training, source data expectations, and data review triggers before sites begin enrollment.",
        "impact_area": "Startup complexity",
    },
}


class RecommendationEngine:
    def __init__(self) -> None:
        self.traceability = TraceabilityEngine()

    def generate(self, features: ProtocolFeatures, top_driver_names: list[str]) -> list[dict[str, Any]]:
        recommendations: list[dict[str, Any]] = []
        seen: set[str] = set()
        for feature_name in top_driver_names:
            if feature_name in seen or feature_name not in RECOMMENDATION_MAP:
                continue
            feature = find_feature(features, feature_name)
            evidence = self.traceability.evidence_for(features, feature_name)
            mapped = RECOMMENDATION_MAP[feature_name]
            recommendations.append(
                {
                    "feature": feature_name,
                    "title": mapped["title"],
                    "action": mapped["action"],
                    "impact_area": mapped["impact_area"],
                    "current_value": feature.value if feature else None,
                    "evidence": evidence.model_dump() if isinstance(evidence, Evidence) else None,
                }
            )
            seen.add(feature_name)
        return recommendations[:8]

    def recommendation_texts_for_dimension(self, driver_names: list[str]) -> list[str]:
        texts = []
        for name in driver_names:
            if name in RECOMMENDATION_MAP:
                texts.append(RECOMMENDATION_MAP[name]["action"])
        return texts[:4]
