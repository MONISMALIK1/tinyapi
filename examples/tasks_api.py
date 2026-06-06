"""A complete CRUD REST service on tinyapi, backed by sqlite3.

    POST   /tasks          create a task            -> 201
    GET    /tasks          list (optional ?done=1)  -> 200
    GET    /tasks/<id>     fetch one                -> 200 / 404
    PUT    /tasks/<id>     replace/patch fields     -> 200 / 404
    DELETE /tasks/<id>     delete                   -> 204 / 404

``build_app(db_path)`` returns a fresh App so tests can wire an in-memory database
and drive it with TestClient; running this module starts a real server.
"""

from __future__ import annotations

from ..app import App
from ..db import Database
from ..errors import HTTPError

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT    NOT NULL,
    done       INTEGER NOT NULL DEFAULT 0,
    created_at TEXT    NOT NULL DEFAULT (datetime('now'))
);
"""


def build_app(db_path: str = ":memory:") -> App:
    db = Database(db_path)
    db.executescript(SCHEMA)
    app = App()
    app.db = db  # handy for tests / introspection

    def get(task_id):
        return db.query_one("SELECT * FROM tasks WHERE id = ?", (task_id,))

    def require(task_id):
        task = get(task_id)
        if task is None:
            raise HTTPError(404, f"task {task_id} not found")
        return task

    @app.post("/tasks")
    def create(req):
        data = req.json() or {}
        title = data.get("title")
        if not isinstance(title, str) or not title.strip():
            raise HTTPError(400, "field 'title' is required and must be a non-empty string")
        new_id = db.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (title.strip(), int(bool(data.get("done", False)))),
        )
        return get(new_id), 201

    @app.get("/tasks")
    def list_tasks(req):
        done = req.query_get("done")
        if done in ("0", "1", "true", "false"):
            flag = 1 if done in ("1", "true") else 0
            return db.query("SELECT * FROM tasks WHERE done = ? ORDER BY id", (flag,))
        return db.query("SELECT * FROM tasks ORDER BY id")

    @app.get("/tasks/<id>")
    def get_one(req):
        return require(req.params["id"])

    @app.route("/tasks/<id>", methods=["PUT", "PATCH"])
    def update(req):
        task = require(req.params["id"])
        data = req.json() or {}
        title = data.get("title", task["title"])
        if not isinstance(title, str) or not title.strip():
            raise HTTPError(400, "field 'title' must be a non-empty string")
        done = int(bool(data.get("done", task["done"])))
        db.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?",
                   (title.strip(), done, task["id"]))
        return get(task["id"])

    @app.delete("/tasks/<id>")
    def delete(req):
        task = require(req.params["id"])
        db.execute("DELETE FROM tasks WHERE id = ?", (task["id"],))
        return None, 204

    return app


if __name__ == "__main__":
    from ..server import run
    run(build_app())
