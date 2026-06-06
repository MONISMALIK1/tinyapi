"""A thin, safe sqlite3 helper.

Everything goes through parameterized queries (``?`` placeholders) — the API never
builds SQL by string interpolation, so injection isn't possible here. Rows come back
as plain dicts (JSON-friendly), and a lock makes a single connection safe to share
across the server's worker threads.
"""

from __future__ import annotations

import sqlite3
import threading


class Database:
    def __init__(self, path: str = ":memory:"):
        self._conn = sqlite3.connect(path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()

    def executescript(self, script: str) -> None:
        """Run a multi-statement script (e.g. migrations / schema)."""
        with self._lock:
            self._conn.executescript(script)
            self._conn.commit()

    def execute(self, sql: str, params: tuple = ()) -> int:
        """Run a write (INSERT/UPDATE/DELETE); return ``lastrowid``."""
        with self._lock:
            cur = self._conn.execute(sql, params)
            self._conn.commit()
            return cur.lastrowid

    def query(self, sql: str, params: tuple = ()) -> list[dict]:
        with self._lock:
            cur = self._conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def query_one(self, sql: str, params: tuple = ()) -> dict | None:
        rows = self.query(sql, params)
        return rows[0] if rows else None

    def close(self) -> None:
        self._conn.close()


__all__ = ["Database"]
