import sys
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from assistant_core import AssistantCore

class AssistantCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.core = AssistantCore(
            memory_path=Path(self.temp.name) / "memory.json",
            learning_path=Path(self.temp.name) / "approved_learning.json",
            conversation_path=Path(self.temp.name) / "history.json",
        )

    def tearDown(self):
        self.temp.cleanup()

    def test_routes_chat_to_chat_workspace(self):
        result = self.core.handle("Hello there")
        self.assertEqual(result["workspace"]["mode"], "chat")
        self.assertTrue(result["answer"])

    def test_remember_is_explicit_and_persistent(self):
        result = self.core.handle("remember that I prefer short explanations")
        self.assertEqual(result["action"], "remember")
        self.assertEqual(self.core.handle("show memory")["memory"],
                         ["I prefer short explanations"])

    def test_preference_is_learned_automatically(self):
        self.core.handle("I prefer short explanations")
        self.assertIn("I prefer short explanations", self.core.memory.list())

    def test_conversation_is_archived_automatically(self):
        self.core.handle("Hello ASTA")
        history = self.core.archive.list()
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[0]["content"], "Hello ASTA")
        self.assertEqual(history[1]["role"], "assistant")

    def test_conversation_history_can_be_cleared(self):
        self.core.handle("Hello ASTA")
        result = self.core.handle("clear conversation history")
        self.assertEqual(result["action"], "clear_conversation_history")
        self.assertEqual(len(self.core.archive.list()), 1)
        self.assertEqual(self.core.archive.list()[0]["role"], "assistant")

    def test_memory_survives_new_assistant_instance(self):
        path = Path(self.temp.name) / "durable.json"
        first = AssistantCore(memory_path=path)
        first.handle("remember that explain one step at a time")
        second = AssistantCore(memory_path=path)
        self.assertEqual(second.memory.list(), ["explain one step at a time"])

    def test_teaching_examples_are_explicit_and_persistent(self):
        result = self.core.handle("teach ASTA: When teaching code, explain each line.")
        self.assertEqual(result["action"], "teach")
        self.assertEqual(len(result["learning"]), 1)
        second = AssistantCore(
            memory_path=Path(self.temp.name) / "memory.json",
            learning_path=Path(self.temp.name) / "approved_learning.json",
            conversation_path=Path(self.temp.name) / "history.json",
        )
        self.assertEqual(second.learning.list(), ["When teaching code, explain each line."])

    def test_learning_can_be_listed_and_removed(self):
        self.core.handle("teach ASTA: Prefer small examples.")
        shown = self.core.handle("show lessons")
        self.assertEqual(shown["action"], "show_learning")
        removed = self.core.handle("forget lesson: Prefer small examples.")
        self.assertEqual(removed["action"], "forget_learning")
        self.assertEqual(removed["learning"], [])

    def test_forget_one_and_all(self):
        self.core.handle("remember that use simple examples")
        self.core.handle("forget: use simple examples")
        self.assertEqual(self.core.memory.list(), [])
        self.core.handle("remember that use simple examples")
        self.core.handle("forget all memories")
        self.assertEqual(self.core.memory.list(), [])

    def test_coding_routes_to_python_lesson(self):
        result = self.core.handle("Teach me Python loops")
        self.assertEqual(result["action"], "python_lesson")
        self.assertIn("For and while loops", result["answer"])

    def test_research_mode_selected_and_search_is_called(self):
        with patch("assistant_core.search_web", return_value=[]) as search:
            result = self.core.handle("research latest science news")
        self.assertEqual(result["workspace"]["mode"], "research")
        self.assertEqual(result["action"], "web_search")
        search.assert_called_once()


    def test_decision_support_uses_supplied_scores(self):
        result = self.core.compare_options(
            [
                {"name": "A", "scores": {"cost": 5, "quality": 3}},
                {"name": "B", "scores": {"cost": 2, "quality": 5}},
            ],
            {"cost": 3, "quality": 1},
        )
        self.assertEqual(result["ranking"][0]["name"], "A")
        self.assertIn("Top-scoring option", result["explanation"])

    def test_analysis_workspace_explains_required_evidence(self):
        result = self.core.handle("Compare these two options")
        self.assertEqual(result["action"], "structured_analysis")
        self.assertIn("1-5 score", result["answer"])
        self.assertIn("reasoning", result)

    def test_planning_workspace_returns_a_transparent_plan(self):
        result = self.core.handle("Help me plan a Python project without paid APIs")
        self.assertEqual(result["workspace"]["mode"], "planning")
        self.assertEqual(result["action"], "structured_plan")
        self.assertIn("Suggested steps", result["answer"])
        self.assertIn("without paid APIs", result["answer"])

    def test_current_lesson_answer_is_only_shown_on_request(self):
        self.core.handle("Teach me Python loops")
        result = self.core.handle("show the answer")
        self.assertEqual(result["action"], "lesson_answer")
        self.assertIn("range(1, 6)", result["answer"])

if __name__ == "__main__":
    unittest.main()
