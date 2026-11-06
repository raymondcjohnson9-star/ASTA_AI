import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brain"))
from adaptive_ui import choose_workspace

class AdaptiveUITests(unittest.TestCase):
    def test_coding_request(self):
        view = choose_workspace("Teach me Python functions")
        self.assertEqual(view["mode"], "coding")
        self.assertTrue(view["show_code_editor"])
    def test_research_request(self):
        view = choose_workspace("Research the latest news about solar energy")
        self.assertEqual(view["mode"], "research")
        self.assertTrue(view["show_sources"])
    def test_analysis_request(self):
        self.assertEqual(choose_workspace("Compare these two options")["mode"], "analysis")
    def test_planning_request(self):
        self.assertEqual(choose_workspace("Help me plan my project")["mode"], "planning")
    def test_default_chat(self):
        self.assertEqual(choose_workspace("Hello ASTA")["mode"], "chat")

if __name__ == "__main__":
    unittest.main()
