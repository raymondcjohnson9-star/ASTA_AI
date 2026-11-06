"""Validate and prepare the Python pattern examples for ASTA_AI."""
import json
from pathlib import Path
from code_pattern_brain import CodePatternBrain

def train():
    brain = CodePatternBrain.from_file("datasets/python_code_examples.json")
    output = Path("models/asta_code_patterns.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(brain.examples, indent=2), encoding="utf-8")
    print(f"Validated {len(brain.examples)} Python code patterns.")
    print(f"Saved pattern index to {output}")

if __name__ == "__main__":
    train()
