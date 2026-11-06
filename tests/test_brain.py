import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))

from perceptron import Perceptron
from neural_network import NeuralNetwork
from trainer import load_examples


class PerceptronTests(unittest.TestCase):
    def test_learns_and_gate(self):
        examples = [([0, 0], 0), ([0, 1], 0), ([1, 0], 0), ([1, 1], 1)]
        model = Perceptron().train(examples)
        for inputs, expected in examples:
            self.assertEqual(model.predict(inputs), expected)


class NeuralNetworkTests(unittest.TestCase):
    def test_learns_xor_pattern(self):
        examples = load_examples()
        model = NeuralNetwork(2, 4, 1)
        model.train(examples, epochs=6000, learning_rate=0.5)
        for inputs, expected in examples:
            self.assertEqual(int(model.predict(inputs)[0] >= 0.5), expected[0])

    def test_saved_model_restores_same_predictions(self):
        examples = load_examples()
        model = NeuralNetwork(2, 4, 1).train(examples, epochs=6000)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.json"
            model.save(path)
            restored = NeuralNetwork.load(path)
            for inputs, _ in examples:
                self.assertEqual(model.predict(inputs), restored.predict(inputs))

    def test_loaded_model_can_continue_training(self):
        examples = load_examples()
        model = NeuralNetwork(2, 4, 1)
        model.train(examples, epochs=100)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.json"
            model.save(path)
            restored = NeuralNetwork.load(path)
            restored.train(examples, epochs=100)
            self.assertEqual(len(restored.predict([0, 1])), 1)


if __name__ == "__main__":
    unittest.main()
