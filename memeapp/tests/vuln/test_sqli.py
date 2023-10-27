from sqlite3 import OperationalError
from memeapp.utils.dbutils import get_user_id_by_username


class TestSqli:
    def test_sqli_on_login(self, client, app):
        """
        An attacker can inject SQL code into the username parameter, and it will get executed.
        """
        try:
            u = "!@#$%^&*()_+-={}|[]\\:\";'<>?,./"
            p = "!@#$%^&*()_+-={}|[]\\:\";'<>?,./"
            response = client.post("/users",
                                   data={"username": u, "password": p, "passwordConfirm": p, "name": u})
            assert response
            with app.app_context():
                uid = get_user_id_by_username(u)
            assert uid > 0
            response = client.post("/login", data={"username": u, "password": p}, follow_redirects=True)
            assert b"home" in response.data
        except OperationalError:
            assert False
