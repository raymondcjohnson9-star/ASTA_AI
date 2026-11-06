import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from text_brain import TextBrain, tokenize

class TextBrainTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "datasets" / "text_training_data.json"
        cls.dataset = json.loads(path.read_text(encoding="utf-8"))
        cls.brain = TextBrain.from_dataset(cls.dataset).train(cls.dataset, epochs=4500)

    def test_tokenize(self):
        self.assertEqual(tokenize("Hello, ASTA!"), ["hello", "asta"])

    def test_learns_each_intent(self):
        cases = {"greeting": "good morning", "question": "who are you",
                 "thanks": "thank you", "farewell": "see you later"}
        for intent, phrase in cases.items():
            self.assertEqual(self.brain.predict(phrase)["intent"], intent)

    def test_unknown_words_do_not_crash(self):
        self.assertIn(self.brain.predict("flibbertigibbet")["intent"], self.brain.labels)

    def test_save_and_load(self):
        before = self.brain.predict("thank you")
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "text_brain.json"
            self.brain.save(path)
            restored = TextBrain.load(path)
            self.assertEqual(before, restored.predict("thank you"))

if __name__ == "__main__":
    unittest.main()
