"""The outgoing HTTP response.

Handlers rarely build these by hand — returning a ``dict``/``list`` (auto-JSON), a
``(data, status)`` tuple, a string, or ``None`` is enough (see ``app._normalize``).
``Response.json`` / ``Response.text`` are here for when you want explicit control.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Response:
    status: int = 200
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)

    @classmethod
    def json(cls, data, status: int = 200, headers: dict | None = None) -> "Response":
        h = {"Content-Type": "application/json"}
        if headers:
            h.update(headers)
        return cls(status=status, body=json.dumps(data).encode("utf-8"), headers=h)

    @classmethod
    def text(cls, text: str, status: int = 200, headers: dict | None = None) -> "Response":
        h = {"Content-Type": "text/plain; charset=utf-8"}
        if headers:
            h.update(headers)
        return cls(status=status, body=text.encode("utf-8"), headers=h)


__all__ = ["Response"]
