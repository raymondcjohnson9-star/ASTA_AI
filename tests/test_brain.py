import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))

from perceptron import Perceptron
from neural_network import NeuralNetwork
from trainer import load_examples


class PerceptronTests(unittest.TestCase):
    def test_learns_and_gate(self):
        examples = [
            ([0, 0], 0),
            ([0, 1], 0),
            ([1, 0], 0),
            ([1, 1], 1),
        ]
        model = Perceptron().train(examples)
        for inputs, expected in examples:
            self.assertEqual(model.predict(inputs), expected)


class NeuralNetworkTests(unittest.TestCase):
    def test_learns_xor_pattern(self):
        examples = load_examples()
        model = NeuralNetwork(input_size=2, hidden_size=4, output_size=1)
        model.train(examples, epochs=6000, learning_rate=0.5)
        for inputs, expected in examples:
            prediction = model.predict(inputs)[0]
            self.assertEqual(int(prediction >= 0.5), expected[0])


if __name__ == "__main__":
    unittest.main()
