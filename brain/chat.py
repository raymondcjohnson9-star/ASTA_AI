"""A simple terminal chat loop for ASTA_AI."""
import json
from pathlib import Path

from text_brain import TextBrain

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets" / "text_training_data.json"
MODEL_PATH = ROOT / "models" / "asta_text_brain.json"


def load_brain(dataset):
    if MODEL_PATH.exists():
        return TextBrain.load(MODEL_PATH)
    print("No trained text model found. Training a starter model now...")
    brain = TextBrain.from_dataset(dataset).train(dataset)
    brain.save(MODEL_PATH)
    return brain


def main():
    dataset = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    brain = load_brain(dataset)
    print("ASTA_AI is ready. Type 'quit' to end the chat.")
    turn = 0
    while True:
        try:
            message = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nASTA_AI: Goodbye!")
            break
        if message.lower() in {"quit", "exit"}:
            print("ASTA_AI: Goodbye!")
            break
        if not message:
            print("ASTA_AI: Type a message and I'll try to respond.")
            continue
        print("ASTA_AI:", brain.respond(message, dataset, turn))
        turn += 1


if __name__ == "__main__":
    main()
