from sqlite3 import OperationalError
from memeapp.tests.testutils import generate_random_string

from memeapp.utils.dbutils import db_execute, db_query, get_db
import os


class TestDbUtils:
    def test_create(self, app):
        with app.app_context():
            # test DB is created
            assert os.path.exists(app.config.get('DATABASE'))

            # test DB has tables
            try:
                db = get_db()
                cur = db.execute("SELECT * from users limit 1")
                results = cur.fetchall()
                cur.close()
            except OperationalError:
                results = False
        assert len(results) == 1

    def test_query(self, app):
        with app.app_context():
            results = db_query("select * from users limit 1", one=True)
            assert len(results) == 4  # number of columns in users table
            results = db_query("select * from users limit 2")
            assert len(results) == 2

    def test_insert(self, app):
        randomUserName = generate_random_string()
        with app.app_context():
            rowid = db_execute(
                f"INSERT INTO users VALUES ('{randomUserName}', '{randomUserName}', '{randomUserName}', 0)")
            result = db_query(f"SELECT rowid FROM users WHERE name='{randomUserName}'", one=True)
        assert result
        assert rowid == result[0]
