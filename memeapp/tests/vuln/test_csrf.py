import io

from memeapp.tests.testutils import create_user, u2, p2
from memeapp.utils.dbutils import db_query


class TestCsrf:
    def test_csrf_on_share(self, client, app):
        """
        The application doesn't require the `application/json` content-type header, so an attacker can force a victim to
        share a meme with the attacker.
        """
        with app.app_context():
            u3 = "horus"
            p3 = "slughorn"
            create_user(u3, p3)
        client.post("/login", data={"username": u3, "password": p3})
        d = {'file': (io.BytesIO(b"<svg>hello</svg>"), "hello.svg"), 'name': "hello.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        # csrf request with text/plain content-type
        client.post(f"/memes/{mid}/shares", data=f"{{\"a=\":\"x\", \"username\": \"{u2}\"}}",
                    headers={"Content-type": "text/plain"})
        with app.app_context():
            result = db_query("SELECT COUNT(*) FROM meme_shares WHERE user=? AND meme=?", (2, mid), one=True)
        assert result[0] == 0
