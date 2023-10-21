from memeapp.conf import constants
from memeapp.utils import cryptoutils
from memeapp.tests.testutils import u1, p1
from memeapp.utils.dbutils import db_query


class TestUsers:
    def test_user_creation(self, client, app):
        u = "jimmy"
        p = "john"
        response = client.post("/users",
                               data={"username": u, "password": p, "passwordConfirm": p, "name": u})
        assert response
        with app.app_context():
            password_hash = db_query(f"SELECT password_hash FROM users WHERE username='{u}'", one=True)
        assert password_hash
        assert cryptoutils.check_password(p, password_hash[0])

    def test_user_login(self, client, app):
        response = client.post("/login", data={"username": u1, "password": p1}, follow_redirects=True)
        assert b"Home" in response.data
