from memeapp.conf.config import SECRET_KEY


class TestForcedBrowsing:
    def test_forced_browsing(self, client, app):
        """
        An attacker can access the admin panel if they aren't authenticated and aren't localhost.
        """
        response = client.get("/admin", environ_base={'REMOTE_ADDR': '1.1.1.1'})
        assert SECRET_KEY.encode() not in response.data
