from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

ExtractionMethod = Literal["rule", "gemini", "inferred", "user_simulation", "fixture"]
RiskLabel = Literal["Low", "Medium", "High"]


class Evidence(BaseModel):
    feature: str
    snippet: str = ""
    page: int | None = None
    section: str | None = None
    confidence: float = Field(default=0.5, ge=0, le=1)
    method: ExtractionMethod = "rule"


class FeatureValue(BaseModel):
    value: Any = None
    confidence: float = Field(default=0.0, ge=0, le=1)
    method: ExtractionMethod = "inferred"
    supporting_snippet: str = ""
    page: int | None = None
    section: str | None = None

    def evidence(self, feature_name: str) -> Evidence:
        return Evidence(
            feature=feature_name,
            snippet=self.supporting_snippet,
            page=self.page,
            section=self.section,
            confidence=self.confidence,
            method=self.method,
        )


class TrialMetadata(BaseModel):
    title: FeatureValue = Field(default_factory=FeatureValue)
    phase: FeatureValue = Field(default_factory=FeatureValue)
    indication: FeatureValue = Field(default_factory=FeatureValue)
    target_population: FeatureValue = Field(default_factory=FeatureValue)
    target_sample_size: FeatureValue = Field(default_factory=FeatureValue)
    number_of_sites: FeatureValue = Field(default_factory=FeatureValue)
    number_of_countries: FeatureValue = Field(default_factory=FeatureValue)
    regions: FeatureValue = Field(default_factory=FeatureValue)


class DesignFeatures(BaseModel):
    number_of_arms: FeatureValue = Field(default_factory=FeatureValue)
    randomized: FeatureValue = Field(default_factory=FeatureValue)
    blinded: FeatureValue = Field(default_factory=FeatureValue)
    adaptive_design: FeatureValue = Field(default_factory=FeatureValue)
    crossover_design: FeatureValue = Field(default_factory=FeatureValue)
    substudies_present: FeatureValue = Field(default_factory=FeatureValue)
    interim_analysis_present: FeatureValue = Field(default_factory=FeatureValue)
    number_primary_endpoints: FeatureValue = Field(default_factory=FeatureValue)
    number_secondary_endpoints: FeatureValue = Field(default_factory=FeatureValue)
    number_exploratory_endpoints: FeatureValue = Field(default_factory=FeatureValue)
    endpoint_novelty_level: FeatureValue = Field(default_factory=FeatureValue)


class EligibilityFeatures(BaseModel):
    inclusion_count: FeatureValue = Field(default_factory=FeatureValue)
    exclusion_count: FeatureValue = Field(default_factory=FeatureValue)
    biomarker_requirement: FeatureValue = Field(default_factory=FeatureValue)
    genomic_testing_requirement: FeatureValue = Field(default_factory=FeatureValue)
    washout_requirement: FeatureValue = Field(default_factory=FeatureValue)
    prior_therapy_restrictions: FeatureValue = Field(default_factory=FeatureValue)
    restrictive_comorbidity_filters: FeatureValue = Field(default_factory=FeatureValue)
    restrictive_demographic_filters: FeatureValue = Field(default_factory=FeatureValue)
    eligibility_restrictiveness_level: FeatureValue = Field(default_factory=FeatureValue)


class ParticipantBurdenFeatures(BaseModel):
    total_visit_count: FeatureValue = Field(default_factory=FeatureValue)
    in_person_visit_count: FeatureValue = Field(default_factory=FeatureValue)
    remote_visit_count: FeatureValue = Field(default_factory=FeatureValue)
    procedure_intensity_level: FeatureValue = Field(default_factory=FeatureValue)
    invasive_procedures_count: FeatureValue = Field(default_factory=FeatureValue)
    travel_burden_flag: FeatureValue = Field(default_factory=FeatureValue)
    diary_or_device_requirement: FeatureValue = Field(default_factory=FeatureValue)
    participant_burden_level: FeatureValue = Field(default_factory=FeatureValue)


class SiteBurdenFeatures(BaseModel):
    specialized_equipment_required: FeatureValue = Field(default_factory=FeatureValue)
    central_lab_complexity: FeatureValue = Field(default_factory=FeatureValue)
    imaging_complexity: FeatureValue = Field(default_factory=FeatureValue)
    pharmacy_handling_complexity: FeatureValue = Field(default_factory=FeatureValue)
    training_or_certification_required: FeatureValue = Field(default_factory=FeatureValue)
    multiple_vendor_dependencies: FeatureValue = Field(default_factory=FeatureValue)
    workflow_fragmentation_level: FeatureValue = Field(default_factory=FeatureValue)
    site_burden_level: FeatureValue = Field(default_factory=FeatureValue)


class OperationalFeatures(BaseModel):
    number_of_assessment_types: FeatureValue = Field(default_factory=FeatureValue)
    number_of_timepoints: FeatureValue = Field(default_factory=FeatureValue)
    safety_reporting_complexity: FeatureValue = Field(default_factory=FeatureValue)
    decentralized_elements_present: FeatureValue = Field(default_factory=FeatureValue)
    oversight_complexity_level: FeatureValue = Field(default_factory=FeatureValue)
    operational_complexity_level: FeatureValue = Field(default_factory=FeatureValue)


class AmendmentRiskFeatures(BaseModel):
    ambiguous_operational_language_flag: FeatureValue = Field(default_factory=FeatureValue)
    internal_inconsistency_flag: FeatureValue = Field(default_factory=FeatureValue)
    excessive_optional_content_flag: FeatureValue = Field(default_factory=FeatureValue)
    high_design_novelty_flag: FeatureValue = Field(default_factory=FeatureValue)
    likely_site_interpretation_variance_flag: FeatureValue = Field(default_factory=FeatureValue)


class ProtocolFeatures(BaseModel):
    trial_metadata: TrialMetadata = Field(default_factory=TrialMetadata)
    design_features: DesignFeatures = Field(default_factory=DesignFeatures)
    eligibility_features: EligibilityFeatures = Field(default_factory=EligibilityFeatures)
    participant_burden_features: ParticipantBurdenFeatures = Field(default_factory=ParticipantBurdenFeatures)
    site_burden_features: SiteBurdenFeatures = Field(default_factory=SiteBurdenFeatures)
    operational_features: OperationalFeatures = Field(default_factory=OperationalFeatures)
    amendment_risk_features: AmendmentRiskFeatures = Field(default_factory=AmendmentRiskFeatures)


class ProtocolSection(BaseModel):
    name: str
    start_page: int
    end_page: int
    heading: str
    confidence: float = Field(default=0.7, ge=0, le=1)
    method: ExtractionMethod = "rule"


class ProtocolPage(BaseModel):
    page: int
    text: str


class ProtocolRecord(BaseModel):
    id: str
    filename: str
    created_at: datetime
    pages: list[ProtocolPage] = Field(default_factory=list)
    section_map: list[ProtocolSection] = Field(default_factory=list)
    features: ProtocolFeatures | None = None
    scores: dict[str, Any] | None = None
    recommendations: list[dict[str, Any]] = Field(default_factory=list)


class TopDriver(BaseModel):
    feature: str
    impact: float
    contribution_percent: float
    value: Any = None
    evidence: Evidence | None = None


class RiskDimension(BaseModel):
    score: int
    label: RiskLabel
    top_drivers: list[TopDriver]
    summary: str
    recommendations: list[str]


class AssessmentResponse(BaseModel):
    protocol_id: str
    overall_feasibility_risk: int
    overall_label: RiskLabel
    risk_dimensions: dict[str, RiskDimension]
    features: dict[str, Any]
    evidence: list[Evidence]
    recommendations: list[dict[str, Any]]


class SimulationRequest(BaseModel):
    overrides: dict[str, Any]

    @field_validator("overrides")
    @classmethod
    def validate_overrides(cls, value: dict[str, Any]) -> dict[str, Any]:
        if not value:
            raise ValueError("At least one simulator override is required")
        return value


class SimulationResponse(BaseModel):
    protocol_id: str
    before: AssessmentResponse
    after: AssessmentResponse
    deltas: dict[str, int]
    applied_overrides: dict[str, Any]


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1500)


class ChatResponse(BaseModel):
    protocol_id: str
    answer: str
    cited_evidence: list[Evidence] = Field(default_factory=list)
    method: Literal["gemini", "fallback"] = "fallback"
    caveat: str = "This assistant explains an early feasibility assessment prototype and does not provide validated clinical trial outcome predictions."
