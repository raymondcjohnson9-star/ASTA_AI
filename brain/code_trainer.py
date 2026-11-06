"""Validate and index ASTA_AI's editable Python lesson dataset."""
from pathlib import Path
try:
    from .code_brain import CodeBrain
except ImportError:
    from code_brain import CodeBrain


def main():
    root = Path(__file__).resolve().parents[1]
    dataset = root / "datasets" / "python_lessons.json"
    model = root / "models" / "asta_python_code_brain.json"
    brain = CodeBrain.from_file(dataset)
    brain.save_index(model)
    print(f"Validated {len(brain.lessons)} Python lessons.")
    print(f"Saved lesson index to {model}")


if __name__ == "__main__":
    main()
