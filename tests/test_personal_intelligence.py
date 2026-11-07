import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from personal_intelligence import build_personal_brief

class PersonalIntelligenceTests(unittest.TestCase):
    def test_summarizes_topics_and_project_mentions(self):
        brief = build_personal_brief(
            ["I'm working on a Python learning app"],
            [{"role": "user", "content": "Help me build an Android app with Python lessons", "created_at": "2026-11-07T10:00:00+00:00"}],
        )
        topics = [x["topic"] for x in brief["themes"]]
        self.assertIn("coding and learning", topics)
        self.assertIn("building projects", topics)
        self.assertEqual(brief["active_projects"], ["I'm working on a Python learning app"])
        self.assertGreaterEqual(brief["conversation_turns_analyzed"], 1)

    def test_ignores_assistant_turns_and_empty_content(self):
        brief = build_personal_brief([], [
            {"role": "assistant", "content": "Python app project"},
            {"role": "user", "content": ""},
        ])
        self.assertEqual(brief["conversation_turns_analyzed"], 0)
        self.assertEqual(brief["active_projects"], [])

if __name__ == "__main__":
    unittest.main()
