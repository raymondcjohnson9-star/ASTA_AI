"""Load the starter dataset and train ASTA_AI's first neural network."""
import json
from pathlib import Path

from neural_network import NeuralNetwork


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "datasets" / "training_data.json"


def load_examples():
    with DATASET_PATH.open("r", encoding="utf-8") as file:
        dataset = json.load(file)
    return [
        (item["inputs"], item["targets"])
        for item in dataset["examples"]
    ]


def main():
    examples = load_examples()
    model = NeuralNetwork(input_size=2, hidden_size=4, output_size=1)
    model.train(examples, epochs=6000, learning_rate=0.5)

    print("ASTA_AI training complete")
    print("Task: learn the XOR pattern")
    for inputs, expected in examples:
        prediction = model.predict(inputs)[0]
        print(
            f"Input: {inputs} | expected: {expected[0]} "
            f"| predicted: {prediction:.3f} "
            f"| rounded: {int(prediction >= 0.5)}"
        )


if __name__ == "__main__":
    main()
