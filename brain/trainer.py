"""Train ASTA_AI and save its learned parameters."""
import json
from pathlib import Path

from neural_network import NeuralNetwork

ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets" / "training_data.json"
MODEL_PATH = ROOT / "models" / "xor_model.json"


def load_examples():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)
    return [(item["inputs"], item["targets"]) for item in dataset["examples"]]


def main():
    examples = load_examples()
    if MODEL_PATH.exists():
        model = NeuralNetwork.load(MODEL_PATH)
        print("Loaded the previous model; continuing training.")
    else:
        model = NeuralNetwork(input_size=2, hidden_size=4, output_size=1)
        print("Created a new model.")

    model.train(examples, epochs=2000, learning_rate=0.5)
    model.save(MODEL_PATH)
    print(f"Training complete. Saved memory to {MODEL_PATH.relative_to(ROOT)}")

    for inputs, expected in examples:
        prediction = model.predict(inputs)[0]
        print(f"{inputs} -> {prediction:.3f} (expected {expected[0]})")


if __name__ == "__main__":
    main()
