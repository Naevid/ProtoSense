from __future__ import annotations

import re

from app.models.schemas import ProtocolPage, ProtocolSection
from app.services.extraction_engine.llm_provider import GeminiProvider


SECTION_ALIASES = {
    "study summary": ["synopsis", "study summary", "protocol summary"],
    "objectives": ["objectives", "study objectives"],
    "endpoints": ["endpoints", "outcome measures"],
    "study design": ["study design", "design"],
    "inclusion criteria": ["inclusion criteria", "key inclusion"],
    "exclusion criteria": ["exclusion criteria", "key exclusion"],
    "schedule of assessments": ["schedule of assessments", "schedule of activities", "soa"],
    "procedures": ["procedures", "study procedures"],
    "safety": ["safety", "adverse events", "safety reporting"],
    "site requirements": ["site requirements", "investigator site", "site qualification"],
    "operational notes": ["operational notes", "study operations", "vendor", "training"],
}


class SectionMapper:
    def __init__(self, provider: GeminiProvider | None = None) -> None:
        self.provider = provider or GeminiProvider()

    async def map_sections(self, pages: list[ProtocolPage]) -> list[ProtocolSection]:
        sections = self._rule_sections(pages)
        if self._coverage_is_sparse(sections):
            refined = await self.provider.refine_sections(pages, sections)
            if refined:
                sections = refined
        return sections

    def _rule_sections(self, pages: list[ProtocolPage]) -> list[ProtocolSection]:
        matches: list[tuple[str, int, str]] = []
        for page in pages:
            lines = [line.strip() for line in page.text.splitlines() if line.strip()]
            for line in lines[:80]:
                normalized = re.sub(r"^\d+(\.\d+)*\s+", "", line.lower()).strip(" :-")
                if len(normalized) > 90:
                    continue
                for canonical, aliases in SECTION_ALIASES.items():
                    if any(alias == normalized or normalized.startswith(alias) for alias in aliases):
                        matches.append((canonical, page.page, line[:120]))
                        break

        deduped: list[tuple[str, int, str]] = []
        seen: set[str] = set()
        for item in matches:
            if item[0] not in seen:
                deduped.append(item)
                seen.add(item[0])

        sections: list[ProtocolSection] = []
        for index, (name, start_page, heading) in enumerate(deduped):
            next_start = deduped[index + 1][1] if index + 1 < len(deduped) else pages[-1].page
            sections.append(
                ProtocolSection(
                    name=name,
                    start_page=start_page,
                    end_page=max(start_page, next_start),
                    heading=heading,
                    confidence=0.78,
                    method="rule",
                )
            )
        if not sections and pages:
            sections.append(
                ProtocolSection(
                    name="study summary",
                    start_page=pages[0].page,
                    end_page=pages[-1].page,
                    heading="Detected full protocol text",
                    confidence=0.35,
                    method="inferred",
                )
            )
        return sections

    def _coverage_is_sparse(self, sections: list[ProtocolSection]) -> bool:
        required = {"study design", "inclusion criteria", "exclusion criteria", "schedule of assessments"}
        present = {section.name for section in sections}
        return len(sections) < 5 or len(required & present) < 2
