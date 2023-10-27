import random
import string
import os
import base64
import pickle

from memeapp.conf.constants import SESSION_TOKEN_NAME

rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))


class TestDeserialization:
    def test_command_execution_on_serialization(self, client, app):
        """
        The application deserializes the session object. The __reduce__ method gets called, resulting in RCE.
        """

        class Session:
            def __reduce__(self):
                return os.system, (f'touch /tmp/{rand}',)

        payload = base64.b64encode(pickle.dumps(Session())).decode()

        try:
            client.set_cookie('localhost', SESSION_TOKEN_NAME, payload)
            client.get("/")
        except:
            pass
        assert not os.path.exists(f'/tmp/{rand}')
