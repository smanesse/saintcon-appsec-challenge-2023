import io
import os

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from memeapp.utils.dbutils import db_query
from memeapp.tests.testutils import u1, p1, u2, p2


class TestMemes:
    def get_driver(self):
        """Sets chrome options for Selenium.
        Chrome options for headless browser is enabled.
        See https://nander.cc/using-selenium-within-a-docker-container
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chromepath = os.environ.get("chromedriver_path")
        if chromepath:
            service = Service(executable_path=chromepath)
            return webdriver.Chrome(options=chrome_options, service=service)
        else:
            return webdriver.Chrome(options=chrome_options)

    def test_meme_upload_download(self, client, app):
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>test_meme_upload_download</svg>"), "test_meme_upload_download.svg"),
             'name': "test_meme_upload_download.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        with app.app_context():
            meme_id, name, owner_id = db_query(f"SELECT rowid, name, owner FROM memes WHERE rowid='{mid}'",
                                               one=True)
        assert str(meme_id) == mid
        assert owner_id == 1
        assert name == "test_meme_upload_download.svg"
        response = client.get(f"memes/{mid}/view")
        assert response.data == b"<svg>test_meme_upload_download</svg>"
        assert response.mimetype == "image/svg+xml"

    def test_meme_share(self, client):
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>test_meme_share</svg>"), "test_meme_share.svg"),
             'name': "test_meme_share.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        response = client.post(f"/memes/{mid}/shares", json={"username": u2})
        assert response.status_code == 201
        client.post("/login", data={"username": u2, "password": p2})
        response = client.get(f"/memes/{mid}/view")
        assert response.status_code == 200
        assert response.data == b"<svg>test_meme_share</svg>"

    def test_view_shared_memes(self, client):
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>test_meme_share</svg>"), "test_meme_share.svg"),
             'name': "test_meme_share.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        response = client.post(f"/memes/{mid}/shares", json={"username": u2})
        assert response.status_code == 201
        client.post("/login", data={"username": u2, "password": p2})
        response = client.get(f"/shared")
        assert response.status_code == 200

    def test_import_meme(self, client):
        driver = self.get_driver()
        driver.get("https://appsec.saintcon.community/meme.html")
        driver.save_screenshot("/tmp/out.png")
        driver.close()
        client.post("/login", data={"username": u1, "password": p1})
        response = client.post("/import", data={"url": "http://appsec.saintcon.community/meme.html", "name": "asdf"})
        mid = response.location.split("/")[-1]
        response = client.get(f"/memes/{mid}/view")
        assert response.status_code == 200
        with open("/tmp/out.png", "rb") as f:
            assert response.data == f.read()
