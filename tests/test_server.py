"""Smoke-test the real http.server adapter over an actual loopback socket."""

import json
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

from tinyapi.examples.tasks_api import build_app
from tinyapi.server import make_handler


class ServerSmokeTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(build_app(":memory:")))
        self.port = self.server.server_address[1]
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()

    def _request(self, method, path, data=None):
        body = json.dumps(data).encode() if data is not None else None
        headers = {"Content-Type": "application/json"} if body else {}
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}{path}",
                                     data=body, method=method, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            raw = resp.read()
            return resp.status, (json.loads(raw) if raw else None)

    def test_create_and_list_over_http(self):
        status, body = self._request("POST", "/tasks", {"title": "over the wire"})
        self.assertEqual(status, 201)
        self.assertEqual(body["title"], "over the wire")

        status, listing = self._request("GET", "/tasks")
        self.assertEqual(status, 200)
        self.assertEqual(len(listing), 1)


if __name__ == "__main__":
    unittest.main()
