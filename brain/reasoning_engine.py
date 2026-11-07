"""Transparent request analysis and planning helpers.

This module structures a user's stated goal without pretending to be a
foundation model. It never invents facts, scores, deadlines, or constraints.
"""
from __future__ import annotations

import re


def analyze_request(request: str) -> dict:
    text = re.sub(r"\s+", " ", str(request or "")).strip()
    if not text:
        raise ValueError("request cannot be empty")

    constraints = []
    patterns = (
        r"\b(?:by|before|until)\s+[^,.!?]+",
        r"\b(?:under|below|within|at least|no more than)\s+[^,.!?]+",
        r"\b(?:must|need to|should|without|using)\s+[^,.!?]+",
    )
    for pattern in patterns:
        constraints.extend(match.group(0).strip() for match in re.finditer(pattern, text, re.I))

    questions = []
    if "?" in text:
        questions.append("Confirm the exact outcome the user expects.")
    if not constraints:
        questions.append("No explicit constraints were detected; ask before assuming budget, timing, or tools.")

    objective = re.sub(r"^[,;:\s]+", "", text)
    return {
        "goal": objective,
        "constraints": list(dict.fromkeys(constraints)),
        "unknowns": questions,
        "steps": [
            "Restate the desired outcome in one clear sentence.",
            "List the available information and the constraints the user actually supplied.",
            "Break the work into small, verifiable steps.",
            "Complete the highest-priority step and check its result.",
            "Review the result against the original goal and explain any remaining gaps.",
        ],
        "verification": "Check each result against the user's stated goal; label assumptions and unresolved questions.",
        "confidence_note": "This is a transparent planning scaffold, not proof that the plan is correct.",
    }


def format_analysis(analysis: dict) -> str:
    lines = ["Goal", analysis["goal"], "", "Suggested steps"]
    lines.extend(f"{index}. {step}" for index, step in enumerate(analysis["steps"], 1))
    lines.extend(["", "Constraints"])
    lines.extend(f"- {item}" for item in analysis["constraints"] or ["None explicitly detected."])
    lines.extend(["", "Questions / unknowns"])
    lines.extend(f"- {item}" for item in analysis["unknowns"] or ["No obvious missing detail detected; review before acting."])
    lines.extend(["", "Verification", analysis["verification"], "", analysis["confidence_note"]])
    return "\n".join(lines)
