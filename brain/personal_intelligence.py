"""Transparent personal-intelligence summaries from user-approved context.

This module reports observable themes and projects; it does not infer sensitive
traits, diagnose behavior, or claim to know the user's intentions.
"""
from __future__ import annotations
from datetime import datetime, timezone

TOPIC_TERMS = {
    "coding and learning": ("python", "kotlin", "code", "program", "learn", "lesson", "github"),
    "building projects": ("app", "project", "build", "develop", "repository", "android"),
    "planning and decisions": ("plan", "goal", "decide", "compare", "recommend", "idea"),
    "research": ("research", "search", "source", "latest", "information"),
}

def build_personal_brief(memory_items, conversation_items, limit=5):
    """Return grounded themes, active project mentions and recent activity."""
    memories = [str(x).strip() for x in (memory_items or []) if str(x).strip()]
    turns = [
        x for x in (conversation_items or [])
        if isinstance(x, dict)
        and x.get("role") == "user"
        and isinstance(x.get("content"), str)
        and x["content"].strip()
    ]
    recent = turns[-100:]
    corpus = " ".join(memories + [x["content"] for x in recent]).casefold()
    themes = []
    for label, words in TOPIC_TERMS.items():
        count = sum(corpus.count(word) for word in words)
        if count:
            themes.append({"topic": label, "mentions": count})
    themes.sort(key=lambda x: (-x["mentions"], x["topic"]))
    projects = []
    seen = set()
    for item in memories:
        low = item.casefold()
        if any(term in low for term in ("working on", "building", "developing", "my project", "my goal")):
            if low not in seen:
                projects.append(item)
                seen.add(low)
    latest = recent[-1] if recent else None
    generated = datetime.now(timezone.utc).isoformat(timespec="seconds")
    suggestions = []
    if projects:
        suggestions.append("Choose one active project and define its next small, verifiable step.")
    if any(x["topic"] == "coding and learning" for x in themes):
        suggestions.append("Keep a short learning log with the concept practised and one example that worked.")
    if any(x["topic"] == "planning and decisions" for x in themes):
        suggestions.append("Write down decision criteria before comparing options.")
    if not suggestions:
        suggestions.append("As more conversations are saved, ASTA can summarize recurring topics here.")
    return {
        "generated_at": generated,
        "conversation_turns_analyzed": len(recent),
        "saved_memories_count": len(memories),
        "themes": themes[:max(1, min(int(limit), 10))],
        "active_projects": projects[:10],
        "latest_user_activity": latest.get("created_at") if latest else None,
        "suggestions": suggestions[:5],
        "limitations": "These are keyword-based observations from saved conversations and memory, not verified facts or psychological conclusions. App-usage totals are not uploaded or analyzed by this server.",
    }
