"""HTTP errors that handlers can raise to short-circuit with a status code."""

from __future__ import annotations

_DEFAULT_MESSAGE = {
    400: "bad request",
    401: "unauthorized",
    403: "forbidden",
    404: "not found",
    405: "method not allowed",
    409: "conflict",
    422: "unprocessable entity",
    500: "internal server error",
}


class HTTPError(Exception):
    """Raise from a handler (or middleware) to return ``status`` with a JSON error.

    >>> raise HTTPError(404, "task 7 not found")
    """

    def __init__(self, status: int, message: str | None = None):
        self.status = status
        self.message = message or _DEFAULT_MESSAGE.get(status, "error")
        super().__init__(f"{status} {self.message}")


__all__ = ["HTTPError"]
