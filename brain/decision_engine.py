"""Transparent, user-directed decision support for ASTA_AI.

This module ranks options from scores and priorities supplied by the user.
It does not make high-stakes decisions or act on the user's behalf.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Mapping, Sequence


@dataclass(frozen=True)
class RankedOption:
    name: str
    score: float
    strengths: tuple[str, ...]
    tradeoffs: tuple[str, ...]


def recommend(
    options: Sequence[Mapping[str, object]],
    weights: Mapping[str, float],
) -> List[RankedOption]:
    """Rank options using 1-5 scores and non-negative criterion weights."""
    if not options:
        raise ValueError("Provide at least one option.")
    if not weights:
        raise ValueError("Provide at least one decision criterion.")
    if any(not isinstance(weight, (int, float)) or weight < 0 for weight in weights.values()):
        raise ValueError("Criterion weights must be non-negative numbers.")
    total_weight = sum(weights.values())
    if total_weight <= 0:
        raise ValueError("At least one criterion must have a positive weight.")

    ranked = []
    for option in options:
        name = option.get("name")
        scores = option.get("scores")
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Every option needs a non-empty name.")
        if not isinstance(scores, Mapping):
            raise ValueError(f"Option {name!r} needs a scores mapping.")

        weighted_total = 0.0
        strengths, tradeoffs = [], []
        for criterion, weight in weights.items():
            if criterion not in scores:
                raise ValueError(f"Option {name!r} is missing score for {criterion!r}.")
            score = scores[criterion]
            if not isinstance(score, (int, float)) or not 1 <= score <= 5:
                raise ValueError("Every criterion score must be between 1 and 5.")
            weighted_total += float(score) * float(weight)
            if score >= 4:
                strengths.append(criterion)
            elif score <= 2:
                tradeoffs.append(criterion)

        ranked.append(RankedOption(
            name=name.strip(),
            score=round(weighted_total / total_weight, 2),
            strengths=tuple(strengths),
            tradeoffs=tuple(tradeoffs),
        ))

    return sorted(ranked, key=lambda item: (-item.score, item.name.casefold()))


def explain_recommendation(ranked: Sequence[RankedOption]) -> str:
    """Create a concise explanation while preserving user choice."""
    if not ranked:
        return "There is not enough information to compare the options."
    best = ranked[0]
    lines = [f"Top-scoring option: {best.name} ({best.score}/5)."]
    if best.strengths:
        lines.append("Strongest areas: " + ", ".join(best.strengths) + ".")
    if best.tradeoffs:
        lines.append("Areas to consider: " + ", ".join(best.tradeoffs) + ".")
    if len(ranked) > 1:
        gap = round(best.score - ranked[1].score, 2)
        lines.append(f"Lead over the next option: {gap} points.")
    lines.append(
        "This comparison uses supplied scores and priorities, not guarantees. "
        "Review the evidence and make the final choice yourself."
    )
    return " ".join(lines)
