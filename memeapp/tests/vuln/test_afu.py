import io
import os

from memeapp.tests.testutils import u1, p1


class TestAfu:
    def test_arbitrary_file_upload(self, client, app):
        """
        An attacker can upload files outside the main upload directory.
        """
        path = os.path.join(app.config["UPLOAD_DIRECTORY"], "../afu_trigger.svg")
        if os.path.exists(path):
            os.remove(path)
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>hello</svg>"), "../afu_trigger.svg"),
             'name': "../afu_trigger.svg"}
        response1 = client.post("/upload", data=d)
        mid = response1.location.split("/")[-1]
        try:
            d = {'file': (io.BytesIO(b"<svg>hello</svg>"), "..././afu_trigger.svg"),
                 'name': "../afu_trigger.svg"}
            client.post("/upload", data=d)
        except FileNotFoundError:
            pass
        with app.app_context():
            assert not os.path.exists(path)

        response = client.get(f"/memes/{mid}/view")
        assert response.data == b"<svg>hello</svg>"
