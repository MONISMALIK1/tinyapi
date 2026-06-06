"""An in-process test client — drive the app without binding a socket.

This is what makes the whole framework (and any app built on it) unit-testable
offline: ``TestClient`` builds a ``Request``, calls ``app.dispatch``, and wraps the
``Response`` with ``.json()`` / ``.text`` / ``.status`` conveniences.
"""

from __future__ import annotations

import json as _json

from .request import Request
from .response import Response


class ClientResponse:
    def __init__(self, resp: Response):
        self.status = resp.status
        self.headers = resp.headers
        self.body = resp.body

    def json(self):
        return _json.loads(self.body.decode("utf-8")) if self.body else None

    @property
    def text(self) -> str:
        return self.body.decode("utf-8")


class TestClient:
    def __init__(self, app):
        self.app = app

    def request(self, method: str, path: str, json=None, body: bytes = b"",
                headers: dict | None = None) -> ClientResponse:
        h = dict(headers or {})
        if json is not None:
            body = _json.dumps(json).encode("utf-8")
            h.setdefault("Content-Type", "application/json")
        req = Request.build(method, path, headers=h, body=body)
        return ClientResponse(self.app.dispatch(req))

    def get(self, path, **kw):
        return self.request("GET", path, **kw)

    def post(self, path, **kw):
        return self.request("POST", path, **kw)

    def put(self, path, **kw):
        return self.request("PUT", path, **kw)

    def patch(self, path, **kw):
        return self.request("PATCH", path, **kw)

    def delete(self, path, **kw):
        return self.request("DELETE", path, **kw)


__all__ = ["TestClient", "ClientResponse"]
