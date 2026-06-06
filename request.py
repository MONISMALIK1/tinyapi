"""The incoming HTTP request, framework-agnostic.

Built once by the server adapter (or the test client) and passed to handlers. The
path query string is parsed up front; the JSON body is parsed lazily and turns a
malformed body into a clean 400 rather than a 500.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from urllib.parse import parse_qs

from .errors import HTTPError


@dataclass
class Request:
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    query: dict[str, list[str]] = field(default_factory=dict)
    body: bytes = b""
    params: dict[str, str] = field(default_factory=dict)  # filled by the router

    @classmethod
    def build(cls, method: str, raw_path: str, headers: dict | None = None,
              body: bytes = b"") -> "Request":
        path, _, qs = raw_path.partition("?")
        return cls(
            method=method.upper(),
            path=path or "/",
            headers={k.lower(): v for k, v in (headers or {}).items()},
            query=parse_qs(qs),
            body=body or b"",
        )

    def json(self):
        """Parse the body as JSON, or raise HTTPError(400) if it's malformed."""
        if not self.body:
            return None
        try:
            return json.loads(self.body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPError(400, f"invalid JSON body: {exc}")

    def query_get(self, key: str, default=None):
        """First value for a query parameter, or ``default``."""
        vals = self.query.get(key)
        return vals[0] if vals else default


__all__ = ["Request"]
