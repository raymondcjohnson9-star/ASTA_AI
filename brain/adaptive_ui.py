"""Task-to-workspace mapping for ASTA_AI's future Android interface.

Returns a UI description; it does not render Android views. The Android frontend
must map these stable workspace identifiers to actual screens and components.
"""
from dataclasses import dataclass, asdict
import re

@dataclass(frozen=True)
class Workspace:
    mode: str
    title: str
    layout: str
    show_code_editor: bool = False
    show_sources: bool = False
    show_task_list: bool = False

WORKSPACES = {
    "chat": Workspace("chat", "Conversation", "chat"),
    "coding": Workspace("coding", "Coding workspace", "lesson_and_editor", True),
    "research": Workspace("research", "Research workspace", "sources_and_summary", False, True),
    "analysis": Workspace("analysis", "Analysis workspace", "evidence_and_findings", False, True),
    "planning": Workspace("planning", "Project workspace", "plan_and_tasks", False, False, True),
}

def choose_workspace(user_request: str) -> dict:
    """Choose a workspace from a request; default safely to normal chat."""
    text = re.sub(r"\s+", " ", str(user_request or "").lower()).strip()
    rules = [
        ("coding", r"\b(code|coding|program|python|java|kotlin|debug|bug|script|function)\b"),
        ("research", r"\b(search|research|look up|find sources|latest news|on the internet|web)\b"),
        ("analysis", r"\b(analy[sz]e|analysis|compare|evaluate|pros and cons|review data)\b"),
        ("planning", r"\b(plan|planning|roadmap|schedule|organize|project steps|to-do)\b"),
    ]
    for mode, pattern in rules:
        if re.search(pattern, text):
            return asdict(WORKSPACES[mode])
    return asdict(WORKSPACES["chat"])
