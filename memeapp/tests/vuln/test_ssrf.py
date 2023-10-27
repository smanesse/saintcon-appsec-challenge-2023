from flask_testing import LiveServerTestCase
from memeapp.app import create_app as ca
from memeapp.tests.conftest import testDB_name, upload_dir
from memeapp.conf.constants import SESSION_TOKEN_NAME
import requests
from PIL import Image
from pytesseract import pytesseract
from memeapp.conf.config import SECRET_KEY


def text_from_image(path="/tmp/out.png"):
    try:
        image = Image.open(path)
        return pytesseract.image_to_string(image)
    except:
        return ""


class TestSSRF(LiveServerTestCase):
    def create_app(self):
        app = ca({
            "TESTING": True,
            "DATABASE": testDB_name,
            "UPLOAD_DIRECTORY": upload_dir,
            "LIVESERVER_PORT": 80,
        })
        return app

    def test_ssrf_simple(self):
        """
        An attacker can make a request to the admin localhost panel and it will get screenshotted.
        read.
        """
        u = "ssrf"
        p = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u, "password": p, "passwordConfirm": p, "name": u}, allow_redirects=False)
        session_token = r.cookies[SESSION_TOKEN_NAME]
        data = {"url": self.get_server_url().replace(":80", "") + "/admin", "name": "teehee"}
        response = requests.post(f"{self.get_server_url()}/import", data=data, allow_redirects=False,
                                 cookies={SESSION_TOKEN_NAME: session_token})

        location = response.headers.get("Location")
        if location:
            mid = response.headers["Location"].split("/")[-1]
            response = requests.get(f"{self.get_server_url()}/memes/{mid}/view",
                                    cookies={SESSION_TOKEN_NAME: session_token}, allow_redirects=False)
            with open("/tmp/out.png", "wb") as f:
                f.write(response.content)
            text = text_from_image("/tmp/out.png")
            assert "729dc" not in text
        else:
            assert True

    def test_ssrf_iframe(self):
        """
        An attacker can make a request to a page with the admin panel iframed and it will get screenshotted.
        read.
        """
        u = "ssrf2"
        p = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u, "password": p, "passwordConfirm": p, "name": u}, allow_redirects=False)
        session_token = r.cookies[SESSION_TOKEN_NAME]
        data = {"url": "https://appsec.saintcon.community/62bb2e00958af832e8e1f408a8b7401a.html", "name": "teehee2"}
        response = requests.post(f"{self.get_server_url()}/import", data=data, allow_redirects=False,
                                 cookies={SESSION_TOKEN_NAME: session_token})

        location = response.headers.get("Location")
        if location:
            mid = response.headers["Location"].split("/")[-1]
            response = requests.get(f"{self.get_server_url()}/memes/{mid}/view",
                                    cookies={SESSION_TOKEN_NAME: session_token}, allow_redirects=False)
            with open("/tmp/out.png", "wb") as f:
                f.write(response.content)
            text = text_from_image("/tmp/out.png")
            assert "729dc" not in text
        else:
            assert True

    def test_ssrf_file(self):
        """
        An attacker can make a request to a file and it will get screenshotted.
        read.
        """
        u = "ssrf3"
        p = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u, "password": p, "passwordConfirm": p, "name": u}, allow_redirects=False)
        session_token = r.cookies[SESSION_TOKEN_NAME]
        data = {"url": "FiLe:///etc/passwd", "name": "teehee3"}
        response = requests.post(f"{self.get_server_url()}/import", data=data, allow_redirects=False,
                                 cookies={SESSION_TOKEN_NAME: session_token})
        location = response.headers.get('location')
        if location:
            mid = location.split("/")[-1]
            response = requests.get(f"{self.get_server_url()}/memes/{mid}/view",
                                    cookies={SESSION_TOKEN_NAME: session_token}, allow_redirects=False)
            with open("/tmp/out.png", "wb") as f:
                f.write(response.content)
            text = text_from_image("/tmp/out.png")
            assert "/usr/sbin/nologin" not in text
        else:
            assert True
