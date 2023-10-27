import io

from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from flask_testing import LiveServerTestCase
from memeapp.app import create_app as ca
from memeapp.tests.conftest import testDB_name, upload_dir
from memeapp.conf.constants import SESSION_TOKEN_NAME
import requests


def get_driver():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    See https://nander.cc/using-selenium-within-a-docker-container
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.set_capability("goog:loggingPrefs", {'browser': 'ALL'})
    service = ChromeService(executable_path="/usr/bin/chromedriver")
    # chrome_options.experimental_options["prefs"] = chrome_prefs
    # chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return webdriver.Chrome(options=chrome_options, service=service)


class TestXSS(LiveServerTestCase):
    def create_app(self):
        app = ca({
            "TESTING": True,
            "DATABASE": testDB_name,
            "UPLOAD_DIRECTORY": upload_dir,
            "LIVESERVER_PORT": 8943,
        })
        return app

    def test_svg_xss_1(self):
        """
        An attacker can upload an SVG file with Javascript and it will be returned
        read.
        """
        u = "svg_xss"
        p = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u, "password": p, "passwordConfirm": p, "name": u}, allow_redirects=False)
        session_token = r.cookies[SESSION_TOKEN_NAME]
        d = {'file': ('xss-test-thing.svg', io.BytesIO(b"""<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
   <polygon id="triangle" points="0,0 0,50 50,0" fill="#009900" stroke="#004400"/>
   <use href="data:image/svg+xml,&lt;svg id='x' xmlns='http://www.w3.org/2000/svg'&gt;&lt;image href='1' onerror='eval(atob(location.hash.slice(1)))' /&gt;&lt;/svg&gt;#x" />
   <script>alert(1)</script>
</svg>
        """))}
        data = {'name': "xss-test-thing.svg"}
        response = requests.post(f"{self.get_server_url()}/upload", data=data, files=d, allow_redirects=False,
                                 cookies={SESSION_TOKEN_NAME: session_token})
        mid = response.headers["Location"].split("/")[-1]
        driver = get_driver()
        driver.get(f"{self.get_server_url()}/")  # to navigate to the domain so the cookie can be set
        driver.add_cookie({"name": SESSION_TOKEN_NAME, "value": session_token})
        try:
            driver.get(f"{self.get_server_url()}/memes/{mid}/view#YWxlcnQoJ2hlbGxvJykK")
            WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                           'timeout')
            alert = driver.switch_to.alert
            alert.accept()
            driver.close()
            assert False
        except TimeoutException:
            assert True

        for entry in driver.get_log('browser'):
            print(entry)

        driver.close()

    def test_comments_xss(self):
        """
        An attacker can add html into their comment and it will be rendered and executed
        read.
        """
        u = "svg_xss2"
        p = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u, "password": p, "passwordConfirm": p, "name": u}, allow_redirects=False)
        session_token = r.cookies[SESSION_TOKEN_NAME]
        d = {'file': ('test.svg', io.BytesIO(b"""<svg></svg>"""))}
        data = {'name': "test.svg"}
        response = requests.post(f"{self.get_server_url()}/upload", data=data, files=d, allow_redirects=False,
                                 cookies={SESSION_TOKEN_NAME: session_token})
        mid = response.headers["Location"].split("/")[-1]
        response = requests.post(f"{self.get_server_url()}/memes/{mid}/comments",
                                 json={"title": "<script>alert(1)</script>hi there<script>alert(1)</script>",
                                       "body": "<img src='/bogus' onerror='alert(1)'>"},
                                 cookies={SESSION_TOKEN_NAME: session_token})
        driver = get_driver()
        driver.get(f"{self.get_server_url()}/")  # to navigate to the domain so the cookie can be set
        driver.add_cookie({"name": SESSION_TOKEN_NAME, "value": session_token})
        driver.get(f"{self.get_server_url()}/memes/{mid}")
        try:
            while True:
                WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                               'timeout')
                alert = driver.switch_to.alert
                alert.accept()
                driver.close()
                assert False
        except TimeoutException:
            assert True

        assert "hi there" in driver.page_source
        assert "onerror" in driver.page_source
        driver.close()

    def test_meme_name_xss(self):
        """
        An attacker inject HTML into their meme name and it will get rendered and executed
        read.
        """

        u = "svg_xss3"
        p = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u, "password": p, "passwordConfirm": p, "name": u}, allow_redirects=False)
        session_token = r.cookies[SESSION_TOKEN_NAME]
        d = {'file': ('test.svg', io.BytesIO(b"""<svg></svg>"""))}
        data = {'name': 'asdf"><img src=x onerror="alert(1)"><br class="'}
        response = requests.post(f"{self.get_server_url()}/upload", data=data, files=d, allow_redirects=False,
                                 cookies={SESSION_TOKEN_NAME: session_token})
        mid = response.headers["Location"].split("/")[-1]

        u2 = "svg_xss4"
        p2 = "asdfadsfasdf"
        r = requests.post(f"{self.get_server_url()}/users",
                          data={"username": u2, "password": p2, "passwordConfirm": p2, "name": u2},
                          allow_redirects=False)
        session_token2 = r.cookies[SESSION_TOKEN_NAME]
        requests.post(f"{self.get_server_url()}/memes/{mid}/shares", json={"username": u2},
                      cookies={SESSION_TOKEN_NAME: session_token})

        driver = get_driver()
        driver.get(f"{self.get_server_url()}/")  # to navigate to the domain so the cookie can be set
        driver.add_cookie({"name": SESSION_TOKEN_NAME, "value": session_token2})
        driver.get(f"{self.get_server_url()}/shared")
        try:
            while True:
                WebDriverWait(driver, 1).until(EC.alert_is_present(),
                                               'timeout')
                alert = driver.switch_to.alert
                alert.accept()
                driver.close()
                assert False
        except TimeoutException:
            assert True

        assert "asdf" in driver.page_source
        assert "onerror" in driver.page_source
        driver.close()