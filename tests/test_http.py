"""Request parsing and Response builders."""

import unittest

from tinyapi.request import Request
from tinyapi.response import Response


class RequestTests(unittest.TestCase):
    def test_splits_path_and_query(self):
        r = Request.build("GET", "/search?q=hello&tag=a&tag=b")
        self.assertEqual(r.path, "/search")
        self.assertEqual(r.query_get("q"), "hello")
        self.assertEqual(r.query.get("tag"), ["a", "b"])

    def test_query_get_default(self):
        r = Request.build("GET", "/x")
        self.assertIsNone(r.query_get("missing"))
        self.assertEqual(r.query_get("missing", "d"), "d")

    def test_headers_lowercased(self):
        r = Request.build("GET", "/", headers={"Content-Type": "application/json"})
        self.assertEqual(r.headers["content-type"], "application/json")

    def test_method_uppercased(self):
        self.assertEqual(Request.build("post", "/").method, "POST")

    def test_json_none_when_empty(self):
        self.assertIsNone(Request.build("POST", "/").json())


class ResponseTests(unittest.TestCase):
    def test_json(self):
        r = Response.json({"a": 1}, status=201)
        self.assertEqual(r.status, 201)
        self.assertEqual(r.headers["Content-Type"], "application/json")
        self.assertIn(b'"a": 1', r.body)

    def test_text(self):
        r = Response.text("hi", status=200)
        self.assertEqual(r.body, b"hi")
        self.assertIn("text/plain", r.headers["Content-Type"])


if __name__ == "__main__":
    unittest.main()
