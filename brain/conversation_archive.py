"""Automatic conversation archive and lightweight preference extraction.

Stores ordinary chat turns automatically for this single-profile prototype.
Obvious credentials are redacted. This is not a secure vault or a multi-user
storage design; use a private persistent volume and protect backups.
"""
from __future__ import annotations
import json
import os
import re
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

MAX_ENTRIES = 10000
RETENTION_DAYS = 180
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_ -]?key|password|passwd|secret|access[_ -]?token)\s*[:=]\s*\S+"),
    re.compile(r"\b(?:sk-[A-Za-z0-9_-]{16,}|AIza[A-Za-z0-9_-]{20,})\b"),
]
_AUTO_MEMORY_PATTERNS = [
    re.compile(r"(?i)\bI prefer\s+(.{3,180})"),
    re.compile(r"(?i)\bI usually\s+(.{3,180})"),
    re.compile(r"(?i)\bmy goal is\s+(.{3,180})"),
    re.compile(r"(?i)\bI'm working on\s+(.{3,180})"),
    re.compile(r"(?i)\bI am working on\s+(.{3,180})"),
]

def redact_secrets(text):
    safe = str(text or "")
    for pattern in _SECRET_PATTERNS:
        safe = pattern.sub("[REDACTED]", safe)
    return safe

class ConversationArchive:
    def __init__(self, path, retention_days=RETENTION_DAYS):
        self.path = Path(path)
        self.retention_days = retention_days
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self):
        try:
            data = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []
        except (OSError, json.JSONDecodeError):
            return []
        return data if isinstance(data, list) else []

    def _save(self, items):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=self.path.name + ".", suffix=".tmp", dir=str(self.path.parent))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(items[-MAX_ENTRIES:], handle, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)

    def append(self, role, content):
        if role not in {"user", "assistant"}:
            raise ValueError("Conversation role must be user or assistant.")
        safe = redact_secrets(str(content or "").strip())
        if not safe:
            return
        items = self._load()
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.retention_days)
        kept = []
        for item in items:
            try:
                stamp = datetime.fromisoformat(item["created_at"])
                if stamp.tzinfo is None:
                    stamp = stamp.replace(tzinfo=timezone.utc)
                if stamp >= cutoff:
                    kept.append(item)
            except (KeyError, TypeError, ValueError):
                continue
        kept.append({"role": role, "content": safe, "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        self._save(kept)

    def list(self, limit=100):
        return self._load()[-max(1, min(int(limit), 500)):]

    def clear(self):
        existed = self.path.exists()
        if existed:
            self.path.unlink()
        return existed

def extract_memory_candidates(text):
    safe = redact_secrets(text)
    found = []
    for pattern in _AUTO_MEMORY_PATTERNS:
        match = pattern.search(safe)
        if match:
            candidate = match.group(0).strip().rstrip(" .!?")
            if len(candidate) >= 8:
                found.append(candidate)
    return list(dict.fromkeys(found))
