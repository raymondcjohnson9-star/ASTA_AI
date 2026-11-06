"""Train ASTA_AI's first text classifier."""
import json
from pathlib import Path
from text_brain import TextBrain

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets" / "text_training_data.json"
MODEL_PATH = ROOT / "models" / "asta_text_brain.json"

def main():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    if MODEL_PATH.exists():
        brain = TextBrain.load(MODEL_PATH)
        print("Loaded saved text brain; continuing training.")
    else:
        brain = TextBrain.from_dataset(dataset)
        print("Created a new text brain.")
    brain.train(dataset)
    brain.save(MODEL_PATH)
    print(f"Saved text brain to {MODEL_PATH.relative_to(ROOT)}")
    for phrase in ("hello there", "who are you", "thank you", "see you later"):
        result = brain.predict(phrase)
        print(f"{phrase!r} -> {result['intent']} ({result['confidence']:.2f})")

if __name__ == "__main__":
    main()
