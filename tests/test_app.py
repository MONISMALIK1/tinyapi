"""Dispatch: return-value normalization, error handling, and middleware."""

import unittest

from tinyapi import App, HTTPError, Response, TestClient


def _app():
    app = App()

    @app.get("/dict")
    def d(req):
        return {"ok": True}

    @app.get("/tuple")
    def t(req):
        return {"x": 1}, 201

    @app.get("/text")
    def tx(req):
        return "hello"

    @app.get("/none")
    def n(req):
        return None

    @app.get("/resp")
    def r(req):
        return Response.json({"explicit": 1}, status=202)

    @app.get("/boom")
    def b(req):
        raise RuntimeError("kaboom-secret-internal")

    @app.get("/err")
    def e(req):
        raise HTTPError(409, "already exists")

    @app.post("/echo")
    def echo(req):
        return req.json()

    return app


class NormalizeTests(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(_app())

    def test_dict_becomes_json_200(self):
        r = self.c.get("/dict")
        self.assertEqual(r.status, 200)
        self.assertEqual(r.json(), {"ok": True})
        self.assertEqual(r.headers["Content-Type"], "application/json")

    def test_tuple_sets_status(self):
        self.assertEqual(self.c.get("/tuple").status, 201)

    def test_string_becomes_text(self):
        self.assertEqual(self.c.get("/text").text, "hello")

    def test_none_becomes_204(self):
        self.assertEqual(self.c.get("/none").status, 204)

    def test_explicit_response_passthrough(self):
        self.assertEqual(self.c.get("/resp").status, 202)


class ErrorTests(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(_app())

    def test_unhandled_exception_is_500_without_leaking(self):
        r = self.c.get("/boom")
        self.assertEqual(r.status, 500)
        self.assertEqual(r.json()["error"], "internal server error")
        self.assertNotIn("kaboom", r.text)

    def test_httperror_status_and_message(self):
        r = self.c.get("/err")
        self.assertEqual(r.status, 409)
        self.assertEqual(r.json()["error"], "already exists")

    def test_404_and_405(self):
        self.assertEqual(self.c.get("/missing").status, 404)
        self.assertEqual(self.c.post("/dict").status, 405)

    def test_echo_roundtrips_json(self):
        self.assertEqual(self.c.post("/echo", json={"a": 1}).json(), {"a": 1})

    def test_malformed_json_is_400(self):
        r = self.c.post("/echo", body=b"{not valid",
                        headers={"Content-Type": "application/json"})
        self.assertEqual(r.status, 400)


class MiddlewareTests(unittest.TestCase):
    def test_runs_outermost_first_and_can_edit_response(self):
        app = App()
        order = []

        @app.use
        def a(req, nxt):
            order.append("a-in")
            resp = nxt(req)
            order.append("a-out")
            resp.headers["X-A"] = "1"
            return resp

        @app.use
        def b(req, nxt):
            order.append("b-in")
            resp = nxt(req)
            order.append("b-out")
            return resp

        @app.get("/")
        def root(req):
            order.append("handler")
            return {"ok": 1}

        r = TestClient(app).get("/")
        self.assertEqual(order, ["a-in", "b-in", "handler", "b-out", "a-out"])
        self.assertEqual(r.headers["X-A"], "1")


if __name__ == "__main__":
    unittest.main()
