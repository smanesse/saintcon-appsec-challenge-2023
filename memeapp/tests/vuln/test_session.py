import base64
import pickle
from dataclasses import dataclass
from datetime import datetime
from memeapp.tests.testutils import u1, p1, u2


@dataclass
class Session:
    timestamp: int
    user_id: int
    signature: str


class TestSession:
    def test_token_verification(self, client, app):
        """
        The application doesn't require the `application/json` content-type header, so an attacker can force a victim to
        share a meme with the attacker.
        """

        def get_session_token(user_id: int, signature: str, ts: int = int(datetime.utcnow().timestamp())):
            session = Session(ts, user_id, signature)
            return base64.b64encode(pickle.dumps(session)).decode().strip()

        fake_token = get_session_token(2, "blah")
        client.post("/login", data={"username": u1, "password": p1})
        response = client.get("/home", headers={"Authorization": fake_token})
        assert u2.encode() not in response.data
        assert u1.encode() in response.data
