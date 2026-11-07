"""Explicit, transparent memory for ASTA_AI with atomic JSON writes."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

MAX_ITEMS = 500
MAX_TEXT_LENGTH = 500

class UserMemory:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []
        return [x for x in data if isinstance(x, dict) and isinstance(x.get("text"), str)]

    def _save(self, items):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=self.path.name + ".", suffix=".tmp", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(items, handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def remember(self, text):
        text = str(text or "").strip()
        if not text or len(text) > MAX_TEXT_LENGTH:
            raise ValueError("A memory must contain 1-500 characters.")
        items = self._load()
        if any(x["text"].casefold() == text.casefold() for x in items):
            return False
        if len(items) >= MAX_ITEMS:
            raise ValueError("Memory is full. Forget an old item before saving another.")
        items.append({"text": text, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        self._save(items)
        return True

    def list(self):
        return [x["text"] for x in self._load() if x.get("text")]

    def search(self, query):
        needle = str(query or "").strip().casefold()
        return [x["text"] for x in self._load() if needle and needle in x["text"].casefold()]

    def forget(self, text=None):
        if text is None:
            existed = self.path.exists()
            if existed:
                self.path.unlink()
            return existed
        target = str(text).strip().casefold()
        items = self._load()
        kept = [x for x in items if x["text"].casefold() != target]
        if len(kept) == len(items):
            return False
        self._save(kept)
        return True
