"""A small feed-forward neural network built with plain Python.

It has one hidden layer and learns by backpropagation. This is an educational
starter model, not a large language model or a general-purpose chatbot.
"""
import math
import random


def sigmoid(value):
    # Keep exp() in a safe range for this small teaching example.
    value = max(-60.0, min(60.0, value))
    return 1.0 / (1.0 + math.exp(-value))


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size=1, seed=42):
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
        hidden = []
        for weights, bias in zip(self.weights_input_hidden, self.bias_hidden):
            total = sum(w * x for w, x in zip(weights, inputs)) + bias
            hidden.append(sigmoid(total))

        outputs = []
        for weights, bias in zip(self.weights_hidden_output, self.bias_output):
            total = sum(w * h for w, h in zip(weights, hidden)) + bias
            outputs.append(sigmoid(total))
        return hidden, outputs

    def predict(self, inputs):
        return self.forward(inputs)[1]

    def train(self, examples, epochs=6000, learning_rate=0.5):
        for _ in range(epochs):
            for inputs, targets in examples:
                hidden, outputs = self.forward(inputs)

                # For sigmoid output units with squared-error training.
                output_deltas = [
                    (target - output) * output * (1.0 - output)
                    for target, output in zip(targets, outputs)
                ]

                hidden_deltas = []
                for hidden_index, hidden_value in enumerate(hidden):
                    downstream = sum(
                        self.weights_hidden_output[out_index][hidden_index]
                        * output_deltas[out_index]
                        for out_index in range(len(output_deltas))
                    )
                    hidden_deltas.append(
                        downstream * hidden_value * (1.0 - hidden_value)
                    )

                # Update output layer.
                for out_index, delta in enumerate(output_deltas):
                    for hidden_index, hidden_value in enumerate(hidden):
                        self.weights_hidden_output[out_index][hidden_index] += (
                            learning_rate * delta * hidden_value
                        )
                    self.bias_output[out_index] += learning_rate * delta

                # Update hidden layer.
                for hidden_index, delta in enumerate(hidden_deltas):
                    for input_index, input_value in enumerate(inputs):
                        self.weights_input_hidden[hidden_index][input_index] += (
                            learning_rate * delta * input_value
                        )
                    self.bias_hidden[hidden_index] += learning_rate * delta
        return self
