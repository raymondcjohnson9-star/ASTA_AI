import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "brain"))
from learning_store import LearningStore

class LearningStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "learning.json"
        self.store = LearningStore(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_teach_and_reload(self):
        self.assertTrue(self.store.teach("When teaching Python, use small examples."))
        self.assertEqual(LearningStore(self.path).list(), ["When teaching Python, use small examples."])

    def test_duplicate_is_not_added(self):
        self.store.teach("Use examples")
        self.assertFalse(self.store.teach("use examples"))
        self.assertEqual(len(self.store.list()), 1)

    def test_forget_one_and_all(self):
        self.store.teach("Example A")
        self.store.teach("Example B")
        self.assertTrue(self.store.forget("Example A"))
        self.assertEqual(self.store.list(), ["Example B"])
        self.assertTrue(self.store.forget())
        self.assertEqual(self.store.list(), [])

    def test_rejects_empty_or_oversized_entry(self):
        with self.assertRaises(ValueError):
            self.store.teach(" ")
        with self.assertRaises(ValueError):
            self.store.teach("x" * 1201)

if __name__ == "__main__":
    unittest.main()
