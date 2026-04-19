from __future__ import annotations

from typing import Any


DIMENSION_NAMES = {
    "startup_complexity": "Startup complexity",
    "enrollment_feasibility": "Enrollment feasibility",
    "participant_burden": "Participant burden",
    "site_execution_burden": "Site execution burden",
    "amendment_susceptibility": "Amendment susceptibility",
}


class ExplanationEngine:
    def summarize(self, dimension: str, score: int, driver_names: list[str]) -> str:
        friendly = DIMENSION_NAMES.get(dimension, dimension.replace("_", " "))
        if not driver_names:
            return f"{friendly} is currently limited based on the extracted protocol features."
        drivers = ", ".join(name.replace("_", " ") for name in driver_names[:3])
        if score >= 67:
            return f"{friendly} is elevated because the protocol combines high-impact drivers including {drivers}."
        if score >= 34:
            return f"{friendly} is moderate, with the main operational pressure coming from {drivers}."
        return f"{friendly} appears lower on the current extraction, with limited contribution from {drivers}."

    def overall_label(self, score: int) -> str:
        if score >= 67:
            return "High"
        if score >= 34:
            return "Medium"
        return "Low"

    def simulation_delta_summary(self, deltas: dict[str, int]) -> str:
        biggest = sorted(deltas.items(), key=lambda item: abs(item[1]), reverse=True)[:2]
        if not biggest:
            return "No material score movement from the selected assumptions."
        readable = ", ".join(f"{key.replace('_', ' ')} {value:+d}" for key, value in biggest)
        return f"The simulated redesign changes risk most in: {readable}."
