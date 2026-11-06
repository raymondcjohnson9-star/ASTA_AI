"""A small feed-forward neural network built with plain Python."""
import json
import math
import random
from pathlib import Path


def sigmoid(value):
    value = max(-60.0, min(60.0, value))
    return 1.0 / (1.0 + math.exp(-value))


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size=1, seed=42):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        rng = random.Random(seed)
        self.weights_input_hidden = [
            [rng.uniform(-1.0, 1.0) for _ in range(input_size)]
            for _ in range(hidden_size)
        ]
        self.bias_hidden = [0.0 for _ in range(hidden_size)]
        self.weights_hidden_output = [
            [rng.uniform(-1.0, 1.0) for _ in range(hidden_size)]
            for _ in range(output_size)
        ]
        self.bias_output = [0.0 for _ in range(output_size)]

    def forward(self, inputs):
        if len(inputs) != self.input_size:
            raise ValueError(f"Expected {self.input_size} inputs, got {len(inputs)}")
        hidden = []
        for weights, bias in zip(self.weights_input_hidden, self.bias_hidden):
            hidden.append(sigmoid(sum(w * x for w, x in zip(weights, inputs)) + bias))
        outputs = []
        for weights, bias in zip(self.weights_hidden_output, self.bias_output):
            outputs.append(sigmoid(sum(w * h for w, h in zip(weights, hidden)) + bias))
        return hidden, outputs

    def predict(self, inputs):
        return self.forward(inputs)[1]

    def train(self, examples, epochs=6000, learning_rate=0.5):
        for _ in range(epochs):
            for inputs, targets in examples:
                hidden, outputs = self.forward(inputs)
                if len(targets) != self.output_size:
                    raise ValueError("Target count does not match output size")
                output_deltas = [
                    (target - output) * output * (1.0 - output)
                    for target, output in zip(targets, outputs)
                ]
                hidden_deltas = []
                for h_index, h_value in enumerate(hidden):
                    downstream = sum(
                        self.weights_hidden_output[o_index][h_index] * output_deltas[o_index]
                        for o_index in range(self.output_size)
                    )
                    hidden_deltas.append(downstream * h_value * (1.0 - h_value))
                for o_index, delta in enumerate(output_deltas):
                    for h_index, h_value in enumerate(hidden):
                        self.weights_hidden_output[o_index][h_index] += learning_rate * delta * h_value
                    self.bias_output[o_index] += learning_rate * delta
                for h_index, delta in enumerate(hidden_deltas):
                    for i_index, value in enumerate(inputs):
                        self.weights_input_hidden[h_index][i_index] += learning_rate * delta * value
                    self.bias_hidden[h_index] += learning_rate * delta
        return self

    def save(self, path):
        """Write architecture and learned parameters to a JSON file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        state = {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "weights_input_hidden": self.weights_input_hidden,
            "bias_hidden": self.bias_hidden,
            "weights_hidden_output": self.weights_hidden_output,
            "bias_output": self.bias_output,
        }
        path.write_text(json.dumps(state, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        """Restore saved parameters so training can continue later."""
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        model = cls(state["input_size"], state["hidden_size"], state["output_size"])
        model.weights_input_hidden = state["weights_input_hidden"]
        model.bias_hidden = state["bias_hidden"]
        model.weights_hidden_output = state["weights_hidden_output"]
        model.bias_output = state["bias_output"]
        return model
