import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brain"))
from decision_engine import recommend, explain_recommendation


class DecisionEngineTests(unittest.TestCase):
    def setUp(self):
        self.options = [
            {"name": "A", "scores": {"cost": 5, "quality": 3}},
            {"name": "B", "scores": {"cost": 2, "quality": 5}},
        ]

    def test_weights_change_ranking(self):
        cost_first = recommend(self.options, {"cost": 3, "quality": 1})
        quality_first = recommend(self.options, {"cost": 1, "quality": 3})
        self.assertEqual(cost_first[0].name, "A")
        self.assertEqual(quality_first[0].name, "B")

    def test_result_has_explanation(self):
        result = recommend(self.options, {"cost": 1, "quality": 1})
        explanation = explain_recommendation(result)
        self.assertIn("Top-scoring option", explanation)
        self.assertIn("final choice", explanation)

    def test_missing_score_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend([{"name": "A", "scores": {"cost": 3}}], {"cost": 1, "quality": 2})

    def test_invalid_score_is_rejected(self):
        with self.assertRaises(ValueError):
            recommend([{"name": "A", "scores": {"cost": 6}}], {"cost": 1})

    def test_empty_options_are_rejected(self):
        with self.assertRaises(ValueError):
            recommend([], {"cost": 1})


if __name__ == "__main__":
    unittest.main()
