import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from assistant_core import AssistantCore

class AssistantCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.core = AssistantCore(memory_path=Path(self.temp.name) / "memory.json")

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

    def test_no_implicit_memory_write(self):
        self.core.handle("I prefer short explanations")
        self.assertEqual(self.core.memory.list(), [])

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

    def test_research_mode_selected_without_network(self):
        result = self.core.handle("research latest science news")
        self.assertEqual(result["workspace"]["mode"], "research")
        self.assertIn(result["action"], {"web_search", "web_search_failed"})

if __name__ == "__main__":
    unittest.main()
