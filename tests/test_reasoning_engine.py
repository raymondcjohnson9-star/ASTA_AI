import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brain"))
from reasoning_engine import analyze_request, format_analysis


class ReasoningEngineTests(unittest.TestCase):
    def test_extracts_user_supplied_constraints(self):
        result = analyze_request("Build a study app under 2 weeks without paid APIs")
        self.assertTrue(any("under 2 weeks" in item for item in result["constraints"]))
        self.assertTrue(any("without paid APIs" in item for item in result["constraints"]))

    def test_does_not_invent_constraints(self):
        result = analyze_request("Help me plan a small project")
        self.assertEqual(result["constraints"], [])
        self.assertTrue(result["unknowns"])

    def test_empty_request_rejected(self):
        with self.assertRaises(ValueError):
            analyze_request("  ")

    def test_formatted_output_contains_verification(self):
        result = format_analysis(analyze_request("Plan a Python learning project"))
        self.assertIn("Verification", result)
        self.assertIn("Suggested steps", result)


if __name__ == "__main__":
    unittest.main()
