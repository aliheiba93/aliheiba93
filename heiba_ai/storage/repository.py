from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from platformdirs import user_data_dir

APP_DIR = Path(user_data_dir("HeibaAI", "ENG Ali Heiba"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


class LocalRepository:
    def __init__(self, root: Path | None = None):
        self.root = Path(root or APP_DIR)
        self.root.mkdir(parents=True, exist_ok=True)
        self.exports = self.root / "exports"
        self.datasets = self.root / "datasets"
        for p in (self.exports, self.datasets / "clips", self.datasets / "annotations"):
            p.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root / "heiba.sqlite3")
        self.db.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        self.db.execute("CREATE TABLE IF NOT EXISTS jobs (id TEXT PRIMARY KEY, input_path TEXT, status TEXT, created_at TEXT, output_dir TEXT)")
        self.db.commit()

    def get_setting(self, key: str, default=None):
        row = self.db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return default if row is None else json.loads(row[0])

    def set_setting(self, key: str, value) -> None:
        self.db.execute("INSERT OR REPLACE INTO settings(key,value) VALUES (?,?)", (key, json.dumps(value)))
        self.db.commit()

    def create_job(self, input_path: Path) -> tuple[str, Path]:
        job_id = str(uuid.uuid4())
        output = self.exports / job_id
        output.mkdir(parents=True, exist_ok=True)
        self.db.execute("INSERT INTO jobs VALUES (?,?,?,?,?)", (job_id, str(input_path), "initialized", datetime.now(timezone.utc).isoformat(), str(output)))
        self.db.commit()
        return job_id, output

    def save_feedback(self, job_id: str, label: str, note: str, input_path: Path | None = None) -> Path:
        record = {"job_id": job_id, "label": label, "note": note, "created_at": datetime.now(timezone.utc).isoformat()}
        target = self.datasets / "feedback.jsonl"
        with target.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
        if input_path and input_path.exists():
            clip = self.datasets / "clips" / f"{job_id}{input_path.suffix.lower()}"
            if not clip.exists():
                clip.write_bytes(input_path.read_bytes())
        annotation = self.datasets / "annotations" / f"{job_id}.json"
        annotation.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        return target
