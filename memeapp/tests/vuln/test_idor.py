import io

from memeapp.tests.testutils import u1, p1, u2, p2


class TestIdor:
    def test_idor(self, client, app):
        """
        An attacker can view arbitrary memes by ID because the authz check users the owner ID instead of the auth'd user
        id.
        """
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>test_idor</svg>"), "test_idor1.svg"),
             'name': "test_idor1.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        client.post("/login", data={"username": u2, "password": p2})
        response = client.get(f"/memes/{mid}/view")
        assert response.status_code != 200
        assert response.data != b"<svg>test_idor</svg>"
