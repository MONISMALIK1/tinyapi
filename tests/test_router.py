"""Route matching: path params, 404 vs 405, and slash boundaries."""

import unittest

from tinyapi.errors import HTTPError
from tinyapi.router import Router


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.r = Router()
        self.r.add(["GET"], "/tasks", "list")
        self.r.add(["POST"], "/tasks", "create")
        self.r.add(["GET", "PUT"], "/tasks/<id>", "one")

    def test_static_match(self):
        handler, params = self.r.match("GET", "/tasks")
        self.assertEqual(handler, "list")
        self.assertEqual(params, {})

    def test_param_match(self):
        handler, params = self.r.match("PUT", "/tasks/42")
        self.assertEqual(handler, "one")
        self.assertEqual(params, {"id": "42"})

    def test_method_is_case_insensitive(self):
        handler, _ = self.r.match("get", "/tasks")
        self.assertEqual(handler, "list")

    def test_unknown_path_404(self):
        with self.assertRaises(HTTPError) as cm:
            self.r.match("GET", "/nope")
        self.assertEqual(cm.exception.status, 404)

    def test_wrong_method_405(self):
        with self.assertRaises(HTTPError) as cm:
            self.r.match("DELETE", "/tasks")
        self.assertEqual(cm.exception.status, 405)

    def test_param_does_not_cross_slash(self):
        with self.assertRaises(HTTPError) as cm:
            self.r.match("GET", "/tasks/1/2")
        self.assertEqual(cm.exception.status, 404)


if __name__ == "__main__":
    unittest.main()
