from memeapp.tests.testutils import generate_random_string
from memeapp.conf.config import SECRET_KEY


class TestMassAssignment:
    def test_mass_assignment(self, client, app):
        """
        An attacker can add the parameter 'a'=(some integer less than 0) to their POST form to create an admin user.
        """
        u = generate_random_string()
        p = generate_random_string()
        response = client.post("/users",
                               data={"username": u, "password": p, "passwordConfirm": p, "name": u, "a": -1})

        response = client.get("/admin", environ_base={'REMOTE_ADDR': '1.1.1.1'})
        assert SECRET_KEY.encode() not in response.data
