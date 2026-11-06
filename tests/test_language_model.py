import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brain"))
from language_model import NeuralLanguageModel, tokenize

class NeuralLanguageModelTests(unittest.TestCase):
    def test_tokenizer(self):
        self.assertEqual(tokenize("Hello, ASTA!"), ["hello", ",", "asta", "!"])

    def test_training_reduces_loss_on_tiny_corpus(self):
        text = "the cat sleeps. the dog runs. the cat runs."
        model = NeuralLanguageModel.from_text(text, embedding_size=8, seed=3)
        model.train(text, epochs=35, learning_rate=0.08)
        self.assertLess(model.loss_history[-1], model.loss_history[0])

    def test_generation_returns_text(self):
        text = "learn and grow. learn every day. practice and grow."
        model = NeuralLanguageModel.from_text(text, embedding_size=8)
        model.train(text, epochs=8)
        result = model.generate("learn", max_tokens=5)
        self.assertIsInstance(result, str)
        self.assertTrue(result.startswith("learn"))

    def test_save_and_load(self):
        text = "small models learn patterns. models predict words."
        model = NeuralLanguageModel.from_text(text, embedding_size=6)
        model.train(text, epochs=2)
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "model.json"
            model.save(path)
            restored = NeuralLanguageModel.load(path)
            self.assertEqual(restored.vocabulary, model.vocabulary)
            self.assertEqual(restored.generate("small", 3), model.generate("small", 3))

    def test_unknown_token_is_safe(self):
        text = "we learn patterns. we study examples."
        model = NeuralLanguageModel.from_text(text, embedding_size=6)
        model.train(text, epochs=2)
        self.assertIsInstance(model.next_token("not-in-vocabulary"), str)

if __name__ == "__main__":
    unittest.main()
