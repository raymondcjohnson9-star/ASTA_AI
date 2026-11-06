"""Static Python pattern analysis and example retrieval. Never executes submitted code."""
import ast
import json
from pathlib import Path
from collections import Counter

FEATURE_TYPES = {
    "For", "While", "If", "FunctionDef", "Return", "Assign",
    "Call", "List", "Dict", "Compare", "BoolOp", "Import",
    "ClassDef", "Try", "With", "Lambda"
}

class CodePatternBrain:
    def __init__(self, examples):
        self.examples = examples

    @classmethod
    def from_file(cls, path):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("Examples file must contain a list")
        required = {"id", "title", "description", "code", "tags"}
        for item in data:
            if not isinstance(item, dict) or not required.issubset(item):
                raise ValueError("Each example needs id, title, description, code and tags")
            cls.inspect(item["code"])
        return cls(data)

    @staticmethod
    def inspect(source):
        tree = ast.parse(source)
        counts = Counter(type(node).__name__ for node in ast.walk(tree))
        return {name: counts[name] for name in FEATURE_TYPES if counts[name]}

    def analyze(self, source):
        features = self.inspect(source)
        return {
            "features": features,
            "summary": ", ".join(sorted(features)) if features else "No common Python structures detected"
        }

    def find_similar(self, source, limit=3):
        target = set(self.inspect(source))
        ranked = []
        for example in self.examples:
            features = set(self.inspect(example["code"]))
            union = target | features
            score = len(target & features) / len(union) if union else 0.0
            ranked.append((score, example))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [{"score": round(score, 3), **example}
                for score, example in ranked[:max(0, limit)]]

if __name__ == "__main__":
    brain = CodePatternBrain.from_file("datasets/python_code_examples.json")
    sample = "for item in items:\n    print(item)"
    print(brain.analyze(sample))
    for match in brain.find_similar(sample):
        print(f'{match["title"]}: {match["score"]}')
