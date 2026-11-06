import tempfile
import unittest
from pathlib import Path

from text_generator import TextGenerator


class TextGeneratorTests(unittest.TestCase):
    def setUp(self):
        self.text = "hello there friend\nhello there neighbor\ngood morning friend\n"
        self.generator = TextGenerator(order=2, seed=3).train(self.text)

    def test_learns_training_lines(self):
        self.assertEqual(self.generator.sentence_count, 3)
        self.assertIn(("hello",), self.generator.transitions)

    def test_generates_words(self):
        result = self.generator.generate("hello", max_words=5)
        self.assertTrue(result.startswith("hello"))
        self.assertTrue(all(word.isalpha() for word in result.split()))

    def test_unknown_seed_falls_back_to_training_patterns(self):
        result = self.generator.generate("unseenword", max_words=5)
        self.assertTrue(result)

    def test_empty_training_text_is_rejected(self):
        with self.assertRaises(ValueError):
            TextGenerator().train("  \n")

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "generator.json"
            self.generator.save(path)
            restored = TextGenerator.load(path, seed=3)
            self.assertEqual(self.generator.sentence_count, restored.sentence_count)
            self.assertEqual(
                self.generator.generate("hello"),
                restored.generate("hello"),
            )


if __name__ == "__main__":
    unittest.main()
