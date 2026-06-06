"""The sqlite3 helper: dict rows, lastrowid, and injection safety."""

import unittest

from tinyapi.db import Database


class DbTests(unittest.TestCase):
    def setUp(self):
        self.db = Database(":memory:")
        self.db.executescript("CREATE TABLE t (id INTEGER PRIMARY KEY, name TEXT);")

    def tearDown(self):
        self.db.close()

    def test_insert_returns_lastrowid(self):
        self.assertEqual(self.db.execute("INSERT INTO t (name) VALUES (?)", ("x",)), 1)

    def test_query_one_returns_dict(self):
        self.db.execute("INSERT INTO t (name) VALUES (?)", ("x",))
        self.assertEqual(self.db.query_one("SELECT * FROM t WHERE id = ?", (1,)),
                         {"id": 1, "name": "x"})

    def test_query_returns_list_of_dicts(self):
        self.db.execute("INSERT INTO t (name) VALUES (?)", ("a",))
        self.assertEqual(self.db.query("SELECT * FROM t"), [{"id": 1, "name": "a"}])

    def test_query_one_missing_is_none(self):
        self.assertIsNone(self.db.query_one("SELECT * FROM t WHERE id = ?", (99,)))

    def test_parameterization_blocks_injection(self):
        self.db.execute("INSERT INTO t (name) VALUES (?)", ("a",))
        evil = "x'); DROP TABLE t;--"
        # Passed as a parameter, the payload is data, not SQL — the table survives.
        self.assertEqual(self.db.query("SELECT * FROM t WHERE name = ?", (evil,)), [])
        self.assertEqual(len(self.db.query("SELECT * FROM t")), 1)


if __name__ == "__main__":
    unittest.main()
