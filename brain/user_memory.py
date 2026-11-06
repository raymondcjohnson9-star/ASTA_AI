"""Opt-in, transparent local memory for ASTA_AI.

Nothing is saved unless the user explicitly types a remember command.
Memory is plain JSON, inspectable and deletable by the user.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

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
        return data if isinstance(data, list) else []

    def remember(self, text):
        text = str(text or "").strip()
        if not text or len(text) > 500:
            raise ValueError("A memory must contain 1-500 characters.")
        items = self._load()
        if any(item.get("text", "").casefold() == text.casefold() for item in items):
            return False
        items.append({
            "text": text,
            "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        self.path.write_text(json.dumps(items, indent=2), encoding="utf-8")
        return True

    def list(self):
        return [item.get("text", "") for item in self._load() if item.get("text")]

    def forget(self, text=None):
        if text is None:
            existed = self.path.exists()
            if existed:
                self.path.unlink()
            return existed
        target = str(text).strip().casefold()
        items = self._load()
        kept = [item for item in items if item.get("text", "").casefold() != target]
        changed = len(kept) != len(items)
        if changed:
            self.path.write_text(json.dumps(kept, indent=2), encoding="utf-8")
        return changed
