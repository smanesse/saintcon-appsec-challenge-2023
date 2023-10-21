import os

from memeapp.conf.config import SECRET_KEY
from memeapp.utils import cryptoutils
from memeapp.tests.testutils import generate_random_string, create_user
from memeapp.utils.dbutils import db_query


class TestAdmin:
    def test_admin_panel(self, client, app):
        u = "admin"
        p = u
        with app.app_context():
            uid = create_user(u, p, admin=1)

        client.post("/login", data={"username": u, "password": p})
        test_val = generate_random_string()
        os.environ["TEST_VAL"] = test_val
        response = client.get("/admin")
        assert test_val.encode() in response.data
        assert SECRET_KEY.encode() in response.data

    def test_admin_panel_accessible_from_localhost(self, client, app):
        # admin panel should be available unauthenticated from localhost
        test_val = generate_random_string()
        os.environ["TEST_VAL"] = test_val
        response = client.get("/admin")
        assert test_val.encode() in response.data
        assert SECRET_KEY.encode() in response.data
