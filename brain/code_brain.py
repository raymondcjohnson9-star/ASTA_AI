"""A tiny example-based Python coding tutor. It never executes submitted code."""
import ast
import json
import re
from pathlib import Path


def words(text):
    return set(re.findall(r"[a-z_]+", text.lower()))


class CodeBrain:
    def __init__(self, lessons):
        self.lessons = lessons

    @classmethod
    def from_file(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        lessons = data.get("lessons", [])
        if not lessons:
            raise ValueError("The lesson file must contain at least one lesson.")
        for lesson in lessons:
            required = {"id", "title", "keywords", "explanation", "code", "exercise", "answer"}
            if not required.issubset(lesson):
                raise ValueError("Each lesson must include all required fields.")
            # Parse examples, but never execute them.
            ast.parse(lesson["code"])
            ast.parse(lesson["answer"])
        return cls(lessons)

    def search(self, question):
        query_words = words(question)
        ranked = []
        for lesson in self.lessons:
            searchable = words(" ".join(
                [lesson["title"], lesson["explanation"], " ".join(lesson["keywords"])]
            ))
            score = len(query_words & searchable)
            if score:
                ranked.append((score, lesson))
        ranked.sort(key=lambda item: (-item[0], item[1]["title"]))
        return [lesson for _, lesson in ranked]

    def answer(self, question):
        matches = self.search(question)
        if not matches:
            return None
        return matches[0]

    def save_index(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        index = [
            {"id": lesson["id"], "title": lesson["title"], "keywords": lesson["keywords"]}
            for lesson in self.lessons
        ]
        path.write_text(json.dumps(index, indent=2), encoding="utf-8")
