"""Authenticated HTTP API for ASTA's Android client."""
from __future__ import annotations
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from assistant_core import AssistantCore
from personal_intelligence import build_personal_brief

MAX_BODY_BYTES = 32_000
CORE = AssistantCore(
    memory_path=os.getenv("ASTA_MEMORY_PATH", "models/user_memory.json"),
    learning_path=os.getenv("ASTA_LEARNING_PATH", "models/approved_learning.json"),
    conversation_path=os.getenv("ASTA_CONVERSATION_PATH", "models/conversation_history.json"),
)

class AstaHandler(BaseHTTPRequestHandler):
    server_version = "ASTA_AI_API/1.1"

    def _send(self, status, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _authorized(self):
        expected = os.getenv("ASTA_API_TOKEN", "")
        return bool(expected) and self.headers.get("Authorization", "") == "Bearer " + expected

    def log_message(self, fmt, *args):
        print("ASTA API:", self.address_string(), fmt % args)

    def do_GET(self):
        if self.path == "/health":
            self._send(200, {"ok": True, "service": "ASTA_AI"})
            return
        if self.path in {"/api/memory", "/api/intelligence"}:
            if not self._authorized():
                self._send(401, {"error": "Unauthorized."})
                return
            memory = CORE.memory.list()
            learning = CORE.learning.list()
            history = CORE.archive.list(limit=500)
            payload = {"memory": memory, "learning": learning, "conversation_history": history}
            if self.path == "/api/intelligence":
                payload["personal_brief"] = build_personal_brief(memory, history)
            self._send(200, payload)
            return
        self._send(404, {"error": "Not found"})

    def do_POST(self):
        if self.path != "/api/chat":
            self._send(404, {"error": "Not found"})
            return
        if not self._authorized():
            self._send(401, {"error": "Unauthorized. Check the API token."})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length < 1 or length > MAX_BODY_BYTES:
            self._send(413, {"error": "Message is empty or too large."})
            return
        try:
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            message = data.get("message", "")
            if not isinstance(message, str) or not message.strip():
                raise ValueError("message must be a non-empty string")
            result = CORE.handle(message[:8000])
            self._send(200, {
                "answer": result.get("answer", ""),
                "action": result.get("action", "respond"),
                "workspace": result.get("workspace", {}),
                "sources": result.get("sources", []),
                "memory": result.get("memory", []),
                "learning": result.get("learning", []),
                "conversation_history": result.get("conversation_history", []),
            })
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._send(400, {"error": str(exc)})
        except Exception:
            self._send(500, {"error": "ASTA could not process that request."})

def main():
    token = os.getenv("ASTA_API_TOKEN", "")
    if len(token) < 24:
        raise SystemExit("Set ASTA_API_TOKEN to a random secret of at least 24 characters.")
    host = os.getenv("ASTA_API_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("ASTA_API_PORT", "8765")))
    server = ThreadingHTTPServer((host, port), AstaHandler)
    print(f"ASTA_AI API listening on {host}:{port}")
    print("Use HTTPS through a trusted reverse proxy before exposing this server to the internet.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()

if __name__ == "__main__":
    main()
