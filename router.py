"""Path routing with typed-free path params (``/tasks/<id>``).

Each route's path is compiled once to an anchored regex. ``match`` distinguishes
"no such path" (404) from "path exists, wrong method" (405) — the difference that
separates a correct router from a sloppy one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .errors import HTTPError

_PARAM = re.compile(r"<([a-zA-Z_][a-zA-Z0-9_]*)>")


def _compile(path: str) -> re.Pattern:
    """Turn ``/tasks/<id>`` into ``^/tasks/(?P<id>[^/]+)$`` (literals escaped)."""
    parts: list[str] = []
    last = 0
    for m in _PARAM.finditer(path):
        parts.append(re.escape(path[last:m.start()]))
        parts.append(f"(?P<{m.group(1)}>[^/]+)")
        last = m.end()
    parts.append(re.escape(path[last:]))
    return re.compile("^" + "".join(parts) + "$")


@dataclass
class Route:
    pattern: re.Pattern
    methods: set[str]
    handler: object
    raw: str


class Router:
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add(self, methods, path: str, handler) -> None:
        self.routes.append(Route(_compile(path), {m.upper() for m in methods}, handler, path))

    def match(self, method: str, path: str):
        """Return ``(handler, params)`` or raise HTTPError 404 / 405."""
        method = method.upper()
        allowed: set[str] = set()
        for route in self.routes:
            m = route.pattern.match(path)
            if not m:
                continue
            if method in route.methods:
                return route.handler, m.groupdict()
            allowed |= route.methods
        if allowed:
            raise HTTPError(405, f"method {method} not allowed (try: {', '.join(sorted(allowed))})")
        raise HTTPError(404)


__all__ = ["Router", "Route"]
