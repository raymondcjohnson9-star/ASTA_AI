"""ASTA_AI's first unified orchestration layer.

Connects task routing, opt-in local memory, Python lesson retrieval and public
web search. This is deterministic orchestration around small existing modules,
not a large generative language model.
"""
from __future__ import annotations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
BRAIN_DIR = Path(__file__).resolve().parent
if str(BRAIN_DIR) not in sys.path:
    sys.path.insert(0, str(BRAIN_DIR))

from adaptive_ui import choose_workspace
from user_memory import UserMemory
from web_research import search_web, format_sources, ResearchError
from code_brain import CodeBrain

class AssistantCore:
    def __init__(self, memory_path=None, lessons_path=None):
        self.memory = UserMemory(memory_path or ROOT / "models" / "user_memory.json")
        self.lessons_path = Path(lessons_path or ROOT / "datasets" / "python_lessons.json")
        self.current_lesson = None

    def handle(self, message):
        """Return a UI mode, answer, sources and explicit action metadata."""
        text = str(message or "").strip()
        workspace = choose_workspace(text)
        result = {
            "workspace": workspace,
            "answer": "",
            "sources": [],
            "action": "respond",
            "memory": self.memory.list(),
        }
        if not text:
            result["answer"] = "Tell me what you'd like help with."
            return result

        lowered = text.casefold()
        if lowered in {"show memory", "what do you remember", "list memories"}:
            memories = self.memory.list()
            result["action"] = "show_memory"
            result["answer"] = ("Here is what you explicitly asked me to remember:\n- "
                                + "\n- ".join(memories)) if memories else "You haven't asked me to remember anything yet."
            return result

        if lowered.startswith("remember that ") or lowered.startswith("remember:"):
            item = text[14:].strip() if lowered.startswith("remember that ") else text[9:].strip()
            if not item:
                result["answer"] = "Tell me what you'd like me to remember after 'remember that'."
            else:
                added = self.memory.remember(item)
                result["action"] = "remember"
                result["answer"] = "I'll remember that." if added else "I already have that memory."
            result["memory"] = self.memory.list()
            return result

        if lowered in {"forget memory", "forget all memories", "clear memory"}:
            self.memory.forget()
            result["action"] = "forget_all"
            result["answer"] = "Your local ASTA_AI memory file has been cleared."
            result["memory"] = []
            return result

        if lowered.startswith("forget:"):
            target = text[7:].strip()
            removed = self.memory.forget(target) if target else False
            result["action"] = "forget_one"
            result["answer"] = "That memory was removed." if removed else "I couldn't find that exact memory."
            result["memory"] = self.memory.list()
            return result

        if workspace["mode"] == "research":
            query = text
            for prefix in ("research ", "search the web for ", "search for ", "look up "):
                if lowered.startswith(prefix):
                    query = text[len(prefix):].strip()
                    break
            try:
                found = search_web(query, max_results=5)
                result["sources"] = [
                    {"title": item.title, "url": item.url, "snippet": item.snippet}
                    for item in found
                ]
                result["answer"] = format_sources(found)
                result["action"] = "web_search"
            except (ResearchError, ValueError) as exc:
                result["answer"] = f"I couldn't complete the web search: {exc}"
                result["action"] = "web_search_failed"
            return result

        if workspace["mode"] == "coding":
            try:
                tutor = CodeBrain.from_file(self.lessons_path)
                lesson = tutor.answer(text)
            except (OSError, ValueError, json.JSONDecodeError, SyntaxError) as exc:
                result["answer"] = f"The coding lesson library could not be loaded: {exc}"
                result["action"] = "coding_library_error"
                return result
            if lesson:
                self.current_lesson = lesson
                result["action"] = "python_lesson"
                result["answer"] = (
                    f"{lesson['title']}\n\n{lesson['explanation']}\n\n"
                    f"Example:\n{lesson['code']}\n\n"
                    f"Try this:\n{lesson['exercise']}\n\n"
                    "Ask 'show the answer' when you want the sample solution."
                )
                result["lesson"] = lesson
            else:
                result["answer"] = "I couldn't find a matching lesson in my current Python library. My lesson coverage is limited."
            return result

        if lowered in {"show the answer", "show answer", "give me the answer"}:
            if self.current_lesson:
                result["action"] = "lesson_answer"
                result["answer"] = self.current_lesson["answer"]
            else:
                result["answer"] = "Ask me for a Python lesson first, then request its sample answer."
            return result

        if lowered in {"what can you do", "help", "help me"}:
            result["answer"] = (
                "I can route requests into coding lessons, public web research, "
                "analysis and project-planning workspaces. I can also remember "
                "information only when you explicitly ask me to. My reasoning "
                "and general conversation abilities are still limited."
            )
            return result

        result["answer"] = (
            "I'm still developing my general conversation ability. I can currently "
            "help with the Python lessons in my library, explicit web research, "
            "and task-specific workspaces. Try 'research ...', 'teach me Python "
            "loops', 'help me plan a project', or 'remember that ...'."
        )
        result["action"] = "limited_fallback"
        return result
