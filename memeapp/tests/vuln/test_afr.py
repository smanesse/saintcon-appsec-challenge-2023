import io
import os

from memeapp.tests.testutils import u1, p1


class TestAfr:
    def test_arbitrary_file_read(self, client, app):
        """
        An attacker can name a file to whatever they want, and if the file exists, it won't be overwritten, so it can be
        read.
        """
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>hello</svg>"), "../../../../../../../../../etc/passwd"),
             'name': "../../../../../../../../../etc/passwd"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]

        response = client.get(f"/memes/{mid}/view")
        assert response.data == b"<svg>hello</svg>"
