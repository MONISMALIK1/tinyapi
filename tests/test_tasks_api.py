"""End-to-end CRUD against the bundled tasks API — in-process, no sockets."""

import unittest

from tinyapi import TestClient
from tinyapi.examples.tasks_api import build_app


class TasksApiTests(unittest.TestCase):
    def setUp(self):
        self.c = TestClient(build_app(":memory:"))

    def test_create_then_get(self):
        r = self.c.post("/tasks", json={"title": "ship it"})
        self.assertEqual(r.status, 201)
        body = r.json()
        self.assertEqual(body["title"], "ship it")
        self.assertEqual(body["done"], 0)
        got = self.c.get(f"/tasks/{body['id']}")
        self.assertEqual(got.status, 200)
        self.assertEqual(got.json()["id"], body["id"])

    def test_list_and_done_filter(self):
        self.c.post("/tasks", json={"title": "a"})
        self.c.post("/tasks", json={"title": "b", "done": True})
        self.assertEqual(len(self.c.get("/tasks").json()), 2)
        done = self.c.get("/tasks?done=1").json()
        self.assertEqual([t["title"] for t in done], ["b"])

    def test_update_keeps_other_fields(self):
        tid = self.c.post("/tasks", json={"title": "x"}).json()["id"]
        r = self.c.put(f"/tasks/{tid}", json={"done": True})
        self.assertEqual(r.status, 200)
        self.assertEqual(r.json()["done"], 1)
        self.assertEqual(r.json()["title"], "x")  # untouched

    def test_delete_then_404(self):
        tid = self.c.post("/tasks", json={"title": "x"}).json()["id"]
        self.assertEqual(self.c.delete(f"/tasks/{tid}").status, 204)
        self.assertEqual(self.c.get(f"/tasks/{tid}").status, 404)

    def test_validation_400(self):
        self.assertEqual(self.c.post("/tasks", json={}).status, 400)
        self.assertEqual(self.c.post("/tasks", json={"title": "   "}).status, 400)

    def test_missing_resource_404(self):
        self.assertEqual(self.c.get("/tasks/999").status, 404)
        self.assertEqual(self.c.put("/tasks/999", json={"title": "x"}).status, 404)
        self.assertEqual(self.c.delete("/tasks/999").status, 404)


if __name__ == "__main__":
    unittest.main()
