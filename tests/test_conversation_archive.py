import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from conversation_archive import ConversationArchive, extract_memory_candidates, redact_secrets

class ConversationArchiveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.archive = ConversationArchive(Path(self.temp.name) / "history.json")

    def tearDown(self):
        self.temp.cleanup()

    def test_archives_turns_and_reloads(self):
        self.archive.append("user", "I am building ASTA.")
        self.archive.append("assistant", "Let's work on it.")
        other = ConversationArchive(Path(self.temp.name) / "history.json")
        self.assertEqual(len(other.list()), 2)
        self.assertEqual(other.list()[0]["role"], "user")

    def test_redacts_obvious_credentials(self):
        self.archive.append("user", "my api_key=super-secret-value")
        self.assertIn("[REDACTED]", self.archive.list()[0]["content"])
        self.assertNotIn("super-secret-value", self.archive.list()[0]["content"])

    def test_extracts_preference_candidates_without_auto_promoting(self):
        found = extract_memory_candidates("I prefer short explanations.")
        self.assertEqual(found, ["I prefer short explanations"])

    def test_clear_removes_history(self):
        self.archive.append("user", "hello")
        self.assertTrue(self.archive.clear())
        self.assertEqual(self.archive.list(), [])

if __name__ == "__main__":
    unittest.main()
