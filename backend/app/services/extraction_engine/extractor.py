from __future__ import annotations

import re
from collections import Counter
from typing import Any

from app.models.schemas import ProtocolFeatures, ProtocolPage, ProtocolSection
from app.services.extraction_engine.llm_provider import GeminiProvider
from app.services.feature_schema.utils import make_feature, set_feature


LEVEL_MAP = {"low": 25, "medium": 55, "high": 85}


class FeatureExtractor:
    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    async def extract(self, pages: list[ProtocolPage], sections: list[ProtocolSection]) -> ProtocolFeatures:
        features = ProtocolFeatures()
        full_text = "\n".join(page.text for page in pages)
        section_text = self._section_texts(pages, sections)
        self._extract_metadata(features, pages, full_text, sections)
        self._extract_design(features, full_text, pages, sections)
        self._extract_eligibility(features, section_text, pages)
        self._extract_burden(features, full_text, section_text, pages)
        self._extract_site_and_ops(features, full_text, pages, sections)
        await self._semantic_fill(features, pages, sections)
        return features

    def _extract_metadata(
        self, features: ProtocolFeatures, pages: list[ProtocolPage], full_text: str, sections: list[ProtocolSection]
    ) -> None:
        first_page = pages[0] if pages else ProtocolPage(page=1, text="")
        title = next((line.strip() for line in first_page.text.splitlines() if len(line.strip()) > 20), "Untitled protocol")
        features.trial_metadata.title = make_feature(title, 0.6, "rule", title, first_page.page, "study summary")
        phase = self._regex(full_text, r"\bPhase\s+(I{1,3}|IV|1|2|3|4|I/II|II/III)\b")
        if phase:
            features.trial_metadata.phase = make_feature(phase.group(0), 0.82, "rule", self._snippet(full_text, phase.start()), 1, "study summary")
        sample = self._regex(full_text, r"(?:approximately|about|up to)?\s*(\d{2,5})\s+(?:participants|subjects|patients)\b")
        if sample:
            features.trial_metadata.target_sample_size = make_feature(int(sample.group(1)), 0.78, "rule", self._snippet(full_text, sample.start()), 1, "study summary")
        sites = self._regex(full_text, r"(\d{1,4})\s+(?:clinical\s+)?sites\b")
        if sites:
            features.trial_metadata.number_of_sites = make_feature(int(sites.group(1)), 0.74, "rule", self._snippet(full_text, sites.start()), 1, "study summary")
        countries = self._regex(full_text, r"(\d{1,3})\s+countries\b")
        if countries:
            features.trial_metadata.number_of_countries = make_feature(int(countries.group(1)), 0.74, "rule", self._snippet(full_text, countries.start()), 1, "study summary")
        indication = self._regex(full_text, r"(?:patients|participants)\s+with\s+([^.\n]{5,90})")
        if indication:
            features.trial_metadata.indication = make_feature(indication.group(1).strip(), 0.55, "rule", self._snippet(full_text, indication.start()), 1, "study summary")

    def _extract_design(self, features: ProtocolFeatures, full_text: str, pages: list[ProtocolPage], sections: list[ProtocolSection]) -> None:
        lower = full_text.lower()
        features.design_features.randomized = make_feature("random" in lower, 0.72, "rule", self._keyword_snippet(full_text, "random"), 1, "study design")
        features.design_features.blinded = make_feature(any(w in lower for w in ["double-blind", "single-blind", "blinded"]), 0.72, "rule", self._keyword_snippet(full_text, "blind"), 1, "study design")
        features.design_features.adaptive_design = make_feature("adaptive" in lower, 0.72, "rule", self._keyword_snippet(full_text, "adaptive"), 1, "study design")
        features.design_features.crossover_design = make_feature("crossover" in lower or "cross-over" in lower, 0.72, "rule", self._keyword_snippet(full_text, "cross"), 1, "study design")
        features.design_features.substudies_present = make_feature(any(w in lower for w in ["substudy", "sub-study"]), 0.7, "rule", self._keyword_snippet(full_text, "substud"), 1, "study design")
        features.design_features.interim_analysis_present = make_feature("interim analysis" in lower, 0.72, "rule", self._keyword_snippet(full_text, "interim"), 1, "study design")
        arms = re.findall(r"\b(?:arm|group)\s+[A-Z0-9]", full_text, flags=re.IGNORECASE)
        features.design_features.number_of_arms = make_feature(max(1, len(set(arms)) or (2 if "random" in lower else 1)), 0.62, "rule", self._keyword_snippet(full_text, "arm"), 1, "study design")
        features.design_features.number_primary_endpoints = make_feature(self._endpoint_count(full_text, "primary"), 0.7, "rule", self._keyword_snippet(full_text, "primary endpoint"), 1, "endpoints")
        features.design_features.number_secondary_endpoints = make_feature(self._endpoint_count(full_text, "secondary"), 0.7, "rule", self._keyword_snippet(full_text, "secondary endpoint"), 1, "endpoints")
        features.design_features.number_exploratory_endpoints = make_feature(self._endpoint_count(full_text, "exploratory"), 0.7, "rule", self._keyword_snippet(full_text, "exploratory"), 1, "endpoints")
        novelty = "high" if any(w in lower for w in ["novel endpoint", "digital biomarker", "composite endpoint"]) else "medium" if "exploratory" in lower else "low"
        features.design_features.endpoint_novelty_level = make_feature(novelty, 0.52, "inferred", self._keyword_snippet(full_text, "endpoint"), 1, "endpoints")

    def _extract_eligibility(self, features: ProtocolFeatures, section_text: dict[str, str], pages: list[ProtocolPage]) -> None:
        inclusion = section_text.get("inclusion criteria", "")
        exclusion = section_text.get("exclusion criteria", "")
        inc_count = self._count_list_items(inclusion)
        exc_count = self._count_list_items(exclusion)
        features.eligibility_features.inclusion_count = make_feature(inc_count, 0.8, "rule", inclusion[:500], self._section_page("inclusion criteria", pages), "inclusion criteria")
        features.eligibility_features.exclusion_count = make_feature(exc_count, 0.8, "rule", exclusion[:500], self._section_page("exclusion criteria", pages), "exclusion criteria")
        eligibility_text = f"{inclusion}\n{exclusion}".lower()
        features.eligibility_features.biomarker_requirement = make_feature(any(w in eligibility_text for w in ["biomarker", "marker-positive", "expression", "mutation"]), 0.76, "rule", self._keyword_snippet(eligibility_text, "biomarker"), None, "inclusion criteria")
        features.eligibility_features.genomic_testing_requirement = make_feature(any(w in eligibility_text for w in ["genomic", "genetic", "mutation", "sequencing", "ngs"]), 0.76, "rule", self._keyword_snippet(eligibility_text, "gen"), None, "inclusion criteria")
        features.eligibility_features.washout_requirement = make_feature("washout" in eligibility_text, 0.76, "rule", self._keyword_snippet(eligibility_text, "washout"), None, "exclusion criteria")
        features.eligibility_features.prior_therapy_restrictions = make_feature("prior therapy" in eligibility_text or "previous treatment" in eligibility_text, 0.7, "rule", self._keyword_snippet(eligibility_text, "prior"), None, "exclusion criteria")
        features.eligibility_features.restrictive_comorbidity_filters = make_feature(any(w in eligibility_text for w in ["uncontrolled", "significant cardiovascular", "renal impairment", "hepatic impairment"]), 0.66, "rule", self._keyword_snippet(eligibility_text, "uncontrolled"), None, "exclusion criteria")
        level = "high" if exc_count >= 12 or inc_count >= 10 else "medium" if exc_count >= 7 or inc_count >= 6 else "low"
        features.eligibility_features.eligibility_restrictiveness_level = make_feature(level, 0.62, "inferred", f"{inc_count} inclusion and {exc_count} exclusion criteria detected.", None, "eligibility")

    def _extract_burden(self, features: ProtocolFeatures, full_text: str, section_text: dict[str, str], pages: list[ProtocolPage]) -> None:
        lower = full_text.lower()
        visit_count = len(set(re.findall(r"\bvisit\s+\d+", lower))) or len(set(re.findall(r"\bweek\s+\d+", lower)))
        in_person = max(0, visit_count - len(re.findall(r"\b(remote|telehealth|virtual)\b", lower)))
        remote = len(set(re.findall(r"\b(remote|telehealth|virtual)\s+visit", lower)))
        invasive = len(re.findall(r"\b(biopsy|lumbar puncture|endoscopy|catheter|bone marrow|invasive)\b", lower))
        features.participant_burden_features.total_visit_count = make_feature(visit_count, 0.63, "rule", self._keyword_snippet(full_text, "visit"), None, "schedule of assessments")
        features.participant_burden_features.in_person_visit_count = make_feature(in_person, 0.52, "inferred", "Estimated from total visits minus remote visit mentions.", None, "schedule of assessments")
        features.participant_burden_features.remote_visit_count = make_feature(remote, 0.58, "rule", self._keyword_snippet(full_text, "remote"), None, "schedule of assessments")
        features.participant_burden_features.invasive_procedures_count = make_feature(invasive, 0.72, "rule", self._keyword_snippet(full_text, "biopsy"), None, "procedures")
        features.participant_burden_features.travel_burden_flag = make_feature(any(w in lower for w in ["overnight", "travel", "specialty center"]), 0.58, "rule", self._keyword_snippet(full_text, "travel"), None, "procedures")
        features.participant_burden_features.diary_or_device_requirement = make_feature(any(w in lower for w in ["diary", "wearable", "device", "epro"]), 0.68, "rule", self._keyword_snippet(full_text, "diary"), None, "procedures")
        level = "high" if visit_count >= 12 or invasive >= 3 else "medium" if visit_count >= 7 or invasive >= 1 else "low"
        features.participant_burden_features.procedure_intensity_level = make_feature(level, 0.58, "inferred", "Visit and invasive procedure density heuristic.", None, "procedures")
        features.participant_burden_features.participant_burden_level = make_feature(level, 0.58, "inferred", "Participant burden inferred from visit, procedure, and device requirements.", None, "schedule of assessments")

    def _extract_site_and_ops(self, features: ProtocolFeatures, full_text: str, pages: list[ProtocolPage], sections: list[ProtocolSection]) -> None:
        lower = full_text.lower()
        features.site_burden_features.specialized_equipment_required = make_feature(any(w in lower for w in ["mri", "pet", "specialized equipment", "validated device"]), 0.72, "rule", self._keyword_snippet(full_text, "equipment"), None, "site requirements")
        features.site_burden_features.training_or_certification_required = make_feature(any(w in lower for w in ["certification", "certified", "training required", "site training"]), 0.72, "rule", self._keyword_snippet(full_text, "training"), None, "site requirements")
        features.site_burden_features.multiple_vendor_dependencies = make_feature(len(re.findall(r"\bvendor\b", lower)) >= 2 or "central lab" in lower and "imaging vendor" in lower, 0.64, "rule", self._keyword_snippet(full_text, "vendor"), None, "operational notes")
        features.site_burden_features.central_lab_complexity = make_feature("high" if "central lab" in lower and "ship" in lower else "medium" if "central lab" in lower else "low", 0.58, "inferred", self._keyword_snippet(full_text, "central lab"), None, "procedures")
        features.site_burden_features.imaging_complexity = make_feature("high" if "pet" in lower or "mri" in lower else "medium" if "imaging" in lower else "low", 0.58, "inferred", self._keyword_snippet(full_text, "imaging"), None, "procedures")
        features.site_burden_features.pharmacy_handling_complexity = make_feature("high" if "cold chain" in lower or "hazardous" in lower else "medium" if "pharmacy" in lower else "low", 0.58, "inferred", self._keyword_snippet(full_text, "pharmacy"), None, "site requirements")
        assessment_types = Counter(re.findall(r"\b(ecg|laboratory|lab|imaging|biopsy|pk|questionnaire|vital signs|safety|epro)\b", lower))
        features.operational_features.number_of_assessment_types = make_feature(len(assessment_types), 0.62, "rule", ", ".join(assessment_types.keys()), None, "schedule of assessments")
        timepoints = len(set(re.findall(r"\b(?:day|week|month)\s+\d+", lower)))
        features.operational_features.number_of_timepoints = make_feature(timepoints, 0.66, "rule", self._keyword_snippet(full_text, "week"), None, "schedule of assessments")
        features.operational_features.decentralized_elements_present = make_feature(any(w in lower for w in ["remote visit", "home health", "telehealth", "decentralized"]), 0.72, "rule", self._keyword_snippet(full_text, "remote"), None, "operational notes")
        features.operational_features.safety_reporting_complexity = make_feature("high" if "susar" in lower or "dlt" in lower else "medium" if "serious adverse event" in lower else "low", 0.58, "inferred", self._keyword_snippet(full_text, "adverse"), None, "safety")
        workflow_level = "high" if len(assessment_types) >= 7 or features.site_burden_features.multiple_vendor_dependencies.value else "medium" if len(assessment_types) >= 4 else "low"
        features.site_burden_features.workflow_fragmentation_level = make_feature(workflow_level, 0.58, "inferred", "Assessment type and vendor dependency heuristic.", None, "operational notes")
        features.site_burden_features.site_burden_level = make_feature(workflow_level, 0.58, "inferred", "Site burden inferred from workflows, equipment, and training.", None, "site requirements")
        features.operational_features.oversight_complexity_level = make_feature(workflow_level, 0.56, "inferred", "Oversight complexity inferred from vendors, safety, and assessments.", None, "operational notes")
        features.operational_features.operational_complexity_level = make_feature(workflow_level, 0.56, "inferred", "Operational complexity inferred from assessment density and dependencies.", None, "operational notes")
        features.amendment_risk_features.ambiguous_operational_language_flag = make_feature(any(w in lower for w in ["as appropriate", "if feasible", "where possible", "per investigator discretion"]), 0.72, "rule", self._keyword_snippet(full_text, "as appropriate"), None, "operational notes")
        features.amendment_risk_features.excessive_optional_content_flag = make_feature(lower.count("optional") >= 3, 0.7, "rule", self._keyword_snippet(full_text, "optional"), None, "study design")
        features.amendment_risk_features.high_design_novelty_flag = make_feature(features.design_features.endpoint_novelty_level.value == "high" or features.design_features.adaptive_design.value is True, 0.56, "inferred", "Novel endpoint or adaptive design detected.", None, "study design")
        features.amendment_risk_features.likely_site_interpretation_variance_flag = make_feature(features.amendment_risk_features.ambiguous_operational_language_flag.value or workflow_level == "high", 0.56, "inferred", "Ambiguous language or fragmented workflow can create site variance.", None, "operational notes")
        features.amendment_risk_features.internal_inconsistency_flag = make_feature(False, 0.35, "inferred", "No deterministic internal inconsistency detected.", None, "operational notes")

    async def _semantic_fill(self, features: ProtocolFeatures, pages: list[ProtocolPage], sections: list[ProtocolSection]) -> None:
        context = {
            "sections": [section.model_dump() for section in sections],
            "page_previews": [{"page": p.page, "text": p.text[:2200]} for p in pages[:18]],
        }
        data = await self.provider.semantic_feature_fill(context)
        for feature_name, payload in data.items():
            if not isinstance(payload, dict) or payload.get("value") is None:
                continue
            set_feature(
                features,
                feature_name,
                make_feature(
                    payload.get("value"),
                    float(payload.get("confidence", 0.65)),
                    "gemini",
                    payload.get("supporting_snippet", ""),
                    payload.get("page"),
                    payload.get("section"),
                ),
            )

    def _section_texts(self, pages: list[ProtocolPage], sections: list[ProtocolSection]) -> dict[str, str]:
        result: dict[str, str] = {}
        for section in sections:
            result[section.name] = "\n".join(page.text for page in pages if section.start_page <= page.page <= section.end_page)
        return result

    def _count_list_items(self, text: str) -> int:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        count = sum(1 for line in lines if re.match(r"^(\d+[\).]|[-*]|[a-z][\).])\s+", line.lower()))
        return count or min(20, len([line for line in lines if len(line) > 20]))

    def _endpoint_count(self, text: str, label: str) -> int:
        match = re.search(rf"{label}\s+endpoints?(.{{0,900}})", text, flags=re.IGNORECASE | re.DOTALL)
        if not match:
            return 0
        return max(1, self._count_list_items(match.group(1)))

    def _regex(self, text: str, pattern: str):
        return re.search(pattern, text, flags=re.IGNORECASE)

    def _snippet(self, text: str, index: int) -> str:
        start = max(0, index - 160)
        end = min(len(text), index + 360)
        return " ".join(text[start:end].split())

    def _keyword_snippet(self, text: str, keyword: str) -> str:
        index = text.lower().find(keyword.lower())
        return self._snippet(text, index) if index >= 0 else ""

    def _section_page(self, name: str, pages: list[ProtocolPage]) -> int | None:
        needle = name.split()[0]
        for page in pages:
            if needle in page.text.lower():
                return page.page
        return None
