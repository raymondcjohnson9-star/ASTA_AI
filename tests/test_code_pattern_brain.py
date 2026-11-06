import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brain"))
from code_pattern_brain import CodePatternBrain

DATA = Path(__file__).resolve().parents[1] / "datasets" / "python_code_examples.json"

class CodePatternBrainTests(unittest.TestCase):
    def setUp(self):
        self.brain = CodePatternBrain.from_file(DATA)

    def test_recognizes_loop(self):
        result = self.brain.analyze("for x in values:\n    print(x)")
        self.assertIn("For", result["features"])
        self.assertIn("Call", result["features"])

    def test_recognizes_function(self):
        result = self.brain.analyze("def add(a, b):\n    return a + b")
        self.assertIn("FunctionDef", result["features"])
        self.assertIn("Return", result["features"])

    def test_finds_similar_example(self):
        matches = self.brain.find_similar("for x in values:\n    print(x)")
        self.assertTrue(matches)
        self.assertEqual(matches[0]["id"], "for-loop")

    def test_invalid_syntax_is_rejected(self):
        with self.assertRaises(SyntaxError):
            self.brain.analyze("for x in :")

    def test_does_not_execute_code(self):
        with tempfile.TemporaryDirectory() as folder:
            marker = Path(folder) / "should_not_exist"
            source = f"open({str(marker)!r}, 'w').write('bad')"
            self.brain.analyze(source)
            self.assertFalse(marker.exists())

if __name__ == "__main__":
    unittest.main()
