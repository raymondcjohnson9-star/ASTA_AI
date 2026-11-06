import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from code_brain import CodeBrain


class CodeBrainTests(unittest.TestCase):
    def setUp(self):
        self.lesson_data = {
            "lessons": [{
                "id": "loops",
                "title": "For loops",
                "keywords": ["loop", "for", "repeat", "range"],
                "explanation": "A for loop repeats over items.",
                "code": "for item in range(3):\n    print(item)",
                "exercise": "Print five numbers.",
                "answer": "for item in range(5):\n    print(item)"
            }]
        }
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "lessons.json"
        self.path.write_text(json.dumps(self.lesson_data), encoding="utf-8")
        self.brain = CodeBrain.from_file(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_finds_matching_lesson(self):
        self.assertEqual(self.brain.answer("how do I use a loop?")["id"], "loops")

    def test_unknown_topic_returns_none(self):
        self.assertIsNone(self.brain.answer("tell me about astronomy"))

    def test_rejects_invalid_python_example(self):
        self.lesson_data["lessons"][0]["code"] = "for in:"
        self.path.write_text(json.dumps(self.lesson_data), encoding="utf-8")
        with self.assertRaises(SyntaxError):
            CodeBrain.from_file(self.path)

    def test_builds_saved_index(self):
        output = Path(self.temp.name) / "index.json"
        self.brain.save_index(output)
        saved = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(saved[0]["id"], "loops")


if __name__ == "__main__":
    unittest.main()
