"""tinyapi — a zero-dependency REST API microframework on the Python stdlib.

Routing with path params, middleware, JSON in/out, a sqlite3 helper, a real CRUD
example, and an in-process test client — all on ``http.server`` + ``sqlite3``, with
no third-party packages.

    from tinyapi import App, TestClient

    app = App()

    @app.get("/hello/<name>")
    def hello(req):
        return {"hello": req.params["name"]}

    client = TestClient(app)
    assert client.get("/hello/world").json() == {"hello": "world"}
"""

from __future__ import annotations

__version__ = "0.1.0"

from .app import App
from .db import Database
from .errors import HTTPError
from .request import Request
from .response import Response
from .router import Router
from .server import run
from .testclient import ClientResponse, TestClient

__all__ = [
    "__version__",
    "App", "Request", "Response", "Router", "HTTPError",
    "Database", "TestClient", "ClientResponse", "run",
]
