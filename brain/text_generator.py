"""A small word n-gram phrase generator for learning purposes."""
import json
import random
from collections import defaultdict
from pathlib import Path

try:
    from .text_brain import tokenize
except ImportError:
    from text_brain import tokenize


class TextGenerator:
    def __init__(self, order=2, seed=7):
        if order < 2:
            raise ValueError("order must be at least 2")
        self.order = order
        self.random = random.Random(seed)
        self.transitions = defaultdict(list)
        self.sentence_count = 0

    def train(self, text):
        """Learn which words tend to follow each context from supplied text."""
        self.transitions.clear()
        self.sentence_count = 0
        for line in text.splitlines():
            words = tokenize(line)
            if not words:
                continue
            padded = ["<START>"] * (self.order - 1) + words + ["<END>"]
            for index in range(self.order - 1, len(padded)):
                context = tuple(padded[index - self.order + 1:index])
                self.transitions[context].append(padded[index])
            self.sentence_count += 1
        if not self.transitions:
            raise ValueError("Training text must contain at least one word.")
        return self

    def generate(self, seed_text="", max_words=20):
        """Generate a short phrase by sampling learned next-word patterns."""
        if max_words < 1:
            raise ValueError("max_words must be positive")
        seed_words = tokenize(seed_text)
        context = (["<START>"] * (self.order - 1) + seed_words)[-(self.order - 1):]
        output = list(seed_words)
        for _ in range(max_words):
            key = tuple(context)
            choices = self.transitions.get(key)
            if not choices:
                # If a supplied seed is unfamiliar, restart from learned text.
                context = ["<START>"] * (self.order - 1)
                key = tuple(context)
                choices = self.transitions.get(key)
                if not choices:
                    break
            next_word = self.random.choice(choices)
            if next_word == "<END>":
                break
            output.append(next_word)
            context = (context + [next_word])[-(self.order - 1):]
        return " ".join(output).strip()

    def save(self, path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "order": self.order,
            "sentence_count": self.sentence_count,
            "transitions": [
                {"context": list(context), "next_words": words}
                for context, words in self.transitions.items()
            ],
        }
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path, seed=7):
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        generator = cls(order=data["order"], seed=seed)
        generator.sentence_count = data["sentence_count"]
        for item in data["transitions"]:
            generator.transitions[tuple(item["context"])] = item["next_words"]
        return generator


def main():
    root = Path(__file__).resolve().parents[1]
    training_path = root / "datasets" / "conversation_text.txt"
    model_path = root / "models" / "asta_text_generator.json"
    text = training_path.read_text(encoding="utf-8")
    generator = TextGenerator(order=2).train(text)
    generator.save(model_path)
    print(f"Learned patterns from {generator.sentence_count} training lines.")
    print("Try a few generated phrases:")
    for _ in range(5):
        print("-", generator.generate(max_words=18))


if __name__ == "__main__":
    main()
