import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "brain"))
from language_engine import LanguageEngine, LanguageEngineError
from assistant_core import AssistantCore


class FakeResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.payload


class LanguageEngineTests(unittest.TestCase):
    def test_ollama_request_and_response(self):
        engine = LanguageEngine("ollama", "http://localhost:11434", "small-model")
        with patch("language_engine.urlopen", return_value=FakeResponse(
            {"message": {"content": "Hello from ASTA"}}
        )) as mocked:
            answer = engine.complete([{"role": "user", "content": "Hello"}])
        self.assertEqual(answer, "Hello from ASTA")
        request = mocked.call_args.args[0]
        self.assertTrue(request.full_url.endswith("/api/chat"))
        self.assertEqual(json.loads(request.data)["model"], "small-model")

    def test_openai_compatible_request_uses_auth_header(self):
        engine = LanguageEngine(
            "openai", "https://example.invalid", "hosted-model", api_key="test-secret"
        )
        with patch("language_engine.urlopen", return_value=FakeResponse(
            {"choices": [{"message": {"content": "A useful answer"}}]}
        )) as mocked:
            answer = engine.complete([{"role": "user", "content": "Explain"}])
        self.assertEqual(answer, "A useful answer")
        request = mocked.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer test-secret")

    def test_empty_model_response_raises(self):
        engine = LanguageEngine("ollama", "http://localhost:11434", "small-model")
        with patch("language_engine.urlopen", return_value=FakeResponse({"message": {"content": ""}})):
            with self.assertRaises(LanguageEngineError):
                engine.complete([{"role": "user", "content": "Hi"}])

    def test_environment_without_provider_disables_model(self):
        with patch.dict("os.environ", {}, clear=True):
            self.assertIsNone(LanguageEngine.from_environment())


class AssistantLanguageIntegrationTests(unittest.TestCase):
    def test_general_message_uses_model_and_keeps_short_context(self):
        class FakeEngine:
            def __init__(self):
                self.messages = None

            def complete(self, messages):
                self.messages = messages
                return "I can help explain that."

        with tempfile.TemporaryDirectory() as folder:
            engine = FakeEngine()
            core = AssistantCore(
                memory_path=Path(folder) / "memory.json",
                language_engine=engine,
            )
            result = core.handle("Can you explain a new idea?")
        self.assertEqual(result["action"], "language_model_reply")
        self.assertEqual(result["answer"], "I can help explain that.")
        self.assertEqual(engine.messages[-1]["content"], "Can you explain a new idea?")
        self.assertEqual(engine.messages[0]["role"], "system")

    def test_model_failure_is_reported_without_crashing(self):
        class BrokenEngine:
            def complete(self, messages):
                raise LanguageEngineError("offline")

        with tempfile.TemporaryDirectory() as folder:
            core = AssistantCore(
                memory_path=Path(folder) / "memory.json",
                language_engine=BrokenEngine(),
            )
            result = core.handle("Tell me something interesting")
        self.assertEqual(result["action"], "language_model_unavailable")
        self.assertIn("unavailable", result["answer"].lower())


if __name__ == "__main__":
    unittest.main()
