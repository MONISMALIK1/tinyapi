"""Run the bundled tasks API: ``python -m tinyapi [--port 8000] [--db tasks.db]``."""

from __future__ import annotations

import argparse

from . import __version__
from .examples.tasks_api import build_app
from .server import run


def main() -> int:
    p = argparse.ArgumentParser(prog="tinyapi",
                                description="Run the bundled CRUD tasks API (stdlib only).")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--db", default=":memory:",
                   help="sqlite path; ':memory:' (default) keeps data only while running.")
    args = p.parse_args()
    run(build_app(args.db), host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
