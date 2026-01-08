from __future__ import annotations
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  company TEXT NOT NULL,
  title TEXT NOT NULL,
  location TEXT,
  url TEXT NOT NULL UNIQUE,
  posted_at TEXT,
  description TEXT
);

CREATE TABLE IF NOT EXISTS applications (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  job_url TEXT NOT NULL,
  applied_at TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'draft',
  resume_version TEXT,
  notes TEXT,
  FOREIGN KEY(job_url) REFERENCES jobs(url)
);

CREATE INDEX IF NOT EXISTS idx_jobs_company_title ON jobs(company, title);
CREATE INDEX IF NOT EXISTS idx_apps_status ON applications(status);
"""

class Tracker:
    def __init__(self, db_path: str = "agent.db"):
        self.db_path = Path(db_path)

    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init(self):
        with self.connect() as c:
            c.executescript(SCHEMA)

    def upsert_job(self, job: Dict[str, Any]):
        with self.connect() as c:
            c.execute("""
              INSERT OR IGNORE INTO jobs(source, company, title, location, url, posted_at, description)
              VALUES(?,?,?,?,?,?,?)
            """, (
                job["source"], job["company"], job["title"], job.get("location"),
                job["url"], job.get("posted_at"), job.get("description"),
            ))

    def log_application(self, job_url: str, status: str = "draft", resume_version: Optional[str] = None, notes: str = ""):
        with self.connect() as c:
            c.execute("""
              INSERT INTO applications(job_url, applied_at, status, resume_version, notes)
              VALUES(?,?,?,?,?)
            """, (job_url, datetime.utcnow().isoformat(), status, resume_version, notes))

    def list_applications(self, status: Optional[str] = None) -> List[dict]:
        with self.connect() as c:
            if status:
                rows = c.execute("SELECT * FROM applications WHERE status=? ORDER BY applied_at DESC", (status,)).fetchall()
            else:
                rows = c.execute("SELECT * FROM applications ORDER BY applied_at DESC").fetchall()
        return [dict(r) for r in rows]
