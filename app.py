"""The application object: route registration, middleware, and dispatch.

``dispatch(request) -> Response`` is the whole framework in one method: run the
middleware onion, match a route, call the handler, normalize whatever it returned,
and turn any ``HTTPError`` into a JSON error (and any *other* exception into a 500
without leaking internals). It never touches a socket — the server and the test
client both just call ``dispatch``.
"""

from __future__ import annotations

from .errors import HTTPError
from .request import Request
from .response import Response
from .router import Router


def _to_response(data, status: int, headers) -> Response:
    if isinstance(data, Response):
        return data
    if data is None:
        return Response(status=status or 204, headers=dict(headers or {}))
    if isinstance(data, (dict, list)):
        return Response.json(data, status=status or 200, headers=headers)
    if isinstance(data, (bytes, bytearray)):
        return Response(status=status or 200, body=bytes(data), headers=dict(headers or {}))
    return Response.text(str(data), status=status or 200, headers=headers)


def _normalize(result) -> Response:
    """Accept Response | dict/list | str | bytes | None | (data[, status[, headers]])."""
    if isinstance(result, Response):
        return result
    if isinstance(result, tuple):
        data = result[0] if result else None
        status = result[1] if len(result) > 1 else 0
        headers = result[2] if len(result) > 2 else None
        return _to_response(data, status, headers)
    return _to_response(result, 0, None)


class App:
    def __init__(self) -> None:
        self.router = Router()
        self._middleware = []

    # --- route registration -------------------------------------------------
    def route(self, path: str, methods=("GET",)):
        def deco(fn):
            self.router.add(methods, path, fn)
            return fn
        return deco

    def get(self, path):
        return self.route(path, ["GET"])

    def post(self, path):
        return self.route(path, ["POST"])

    def put(self, path):
        return self.route(path, ["PUT"])

    def patch(self, path):
        return self.route(path, ["PATCH"])

    def delete(self, path):
        return self.route(path, ["DELETE"])

    def use(self, middleware):
        """Register middleware: ``fn(request, call_next) -> Response``.

        Middleware run outermost-first in registration order.
        """
        self._middleware.append(middleware)
        return middleware

    # --- dispatch -----------------------------------------------------------
    def dispatch(self, request: Request) -> Response:
        def core(req: Request) -> Response:
            handler, params = self.router.match(req.method, req.path)
            req.params = params
            return _normalize(handler(req))

        call = core
        for mw in reversed(self._middleware):
            call = (lambda nxt, mw: (lambda req: mw(req, nxt)))(call, mw)

        try:
            return call(request)
        except HTTPError as exc:
            return Response.json({"error": exc.message, "status": exc.status}, status=exc.status)
        except Exception:  # noqa: BLE001 — never leak internals to the client
            return Response.json({"error": "internal server error", "status": 500}, status=500)


__all__ = ["App"]
