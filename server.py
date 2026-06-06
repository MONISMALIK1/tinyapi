"""The only socket-facing code: a stdlib http.server adapter.

It translates a real HTTP request into a ``Request``, calls ``app.dispatch``, and
writes the ``Response`` back. All routing/handling/error logic lives in ``app`` and
is tested without ever opening a port.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .request import Request


def make_handler(app):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "tinyapi"

        def _handle(self) -> None:
            length = int(self.headers.get("Content-Length") or 0)
            body = self.rfile.read(length) if length else b""
            req = Request.build(self.command, self.path,
                                headers={k: v for k, v in self.headers.items()}, body=body)
            resp = app.dispatch(req)

            data = resp.body if isinstance(resp.body, (bytes, bytearray)) else str(resp.body).encode()
            self.send_response(resp.status)
            for k, v in resp.headers.items():
                self.send_header(k, v)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(data)

        do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = do_OPTIONS = _handle

        def log_message(self, *args):  # keep the test/CI output clean
            pass

    return Handler


def run(app, host: str = "127.0.0.1", port: int = 8000) -> None:
    server = ThreadingHTTPServer((host, port), make_handler(app))
    print(f"tinyapi serving on http://{host}:{port}  (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


__all__ = ["run", "make_handler"]
