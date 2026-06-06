# tinyapi

[![tests](https://github.com/MONISMALIK1/tinyapi/actions/workflows/test.yml/badge.svg)](https://github.com/MONISMALIK1/tinyapi/actions/workflows/test.yml)

A **zero-dependency REST API microframework** built entirely on the Python standard
library — `http.server` for the wire, `sqlite3` for storage. Routing with path
params, middleware, JSON in/out, clean error handling, and an **in-process test
client** so the whole thing (and any app you build on it) is unit-testable without
opening a socket. No Flask, no FastAPI, no third-party packages at all.

## 60-second tour

```python
from tinyapi import App, TestClient

app = App()

@app.get("/hello/<name>")
def hello(req):
    return {"hello": req.params["name"]}        # dict -> 200 JSON

@app.post("/echo")
def echo(req):
    return req.json(), 201                       # (data, status) tuple

# Drive it without a server — perfect for tests:
client = TestClient(app)
assert client.get("/hello/world").json() == {"hello": "world"}
assert client.post("/echo", json={"a": 1}).status == 201
```

Run the bundled CRUD service for real:

```bash
python -m tinyapi --port 8000          # or: make serve

curl -s -XPOST localhost:8000/tasks -d '{"title":"ship it"}'
curl -s localhost:8000/tasks
curl -s localhost:8000/tasks/1
curl -s -XPUT localhost:8000/tasks/1 -d '{"done":true}'
curl -s -XDELETE localhost:8000/tasks/1 -i      # 204
```

## What's in the box

| Module | Responsibility |
| --- | --- |
| `router.py` | path routing with `<param>` capture; **404 vs 405** done right |
| `request.py` / `response.py` | request parsing (query, headers, lazy JSON → clean 400) + response builders |
| `app.py` | `dispatch()` — middleware onion, return-value normalization, error handling |
| `testclient.py` | in-process client (`.get/.post/...` → `.status`, `.json()`) — **no sockets** |
| `db.py` | a small, **always-parameterized** sqlite3 helper (dict rows, injection-safe) |
| `server.py` | the *only* socket-facing code: a thin `http.server` adapter |
| `examples/tasks_api.py` | a complete CRUD service: `POST/GET/PUT/DELETE /tasks` |

## Design choices worth noting

- **Handlers return whatever's convenient.** A `dict`/`list` becomes JSON, a `str`
  becomes text, `None` becomes `204`, a `(data, status)` tuple sets the code, or
  return a `Response` for full control.
- **Errors are first-class.** `raise HTTPError(404, "task 7 not found")` from
  anywhere; unexpected exceptions become a generic `500` that **never leaks**
  internals or stack traces to the client.
- **Middleware is a simple onion.** `fn(request, call_next) -> Response`, run
  outermost-first — enough for logging, auth, CORS, timing.
- **Testable by construction.** The server is a thin adapter over `dispatch()`; the
  `TestClient` calls `dispatch()` directly, so routing, validation, and persistence
  are all tested in-process. (A separate smoke test still exercises a real socket.)
- **Injection-safe storage.** Every query goes through `?` placeholders — the code
  never interpolates values into SQL.

## Install

No third-party dependencies. Python 3.11+.

```bash
git clone https://github.com/MONISMALIK1/tinyapi.git
cd tinyapi && pip install -e .      # optional; or just run from the parent dir
```

## Test

```bash
make test        # or: python -m unittest discover -s tinyapi/tests -t . -v
```

36 tests: routing (params, 404/405), dispatch + normalization + middleware order,
error hiding, request/response parsing, the sqlite helper (incl. an injection
attempt), the full Tasks CRUD via `TestClient`, and a real-socket smoke test.

## Scope & limitations

`tinyapi` is a compact, readable framework — not a production web server. It has no
TLS, auth, async, or templating, and `http.server` is single-process. It's ideal for
internal tools, prototypes, learning how a web framework works end to end, and small
services where "zero dependencies" matters more than throughput.

## License

MIT
