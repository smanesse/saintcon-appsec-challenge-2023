from memeapp.tests.testutils import generate_random_string


# TODO: move all of the error messages to a constant file or i18n translation file so they do not drift from the validation file
class TestRegistrationValidation:

    def test_username_supplied(self, client, app):
        response = client.post("/users", data={
            "username": "",
            "name": "aTester",
            "password": "a",
            "passwordConfirm": "a",
        })

        print(response.data)

        assert b"No username provided" in response.data

    def test_name_supplied(self, client, app):
        response = client.post("/users", data={
            "username": generate_random_string(),
            "name": "",
            "password": "a",
            "passwordConfirm": "a",
        })

        assert b"Name is required" in response.data

    def test_password_supplied(self, client, app):
        response = client.post("/users", data={
            "username": generate_random_string(),
            "name": "aTester",
            "password": "",
            "passwordConfirm": "",
        })

        assert b"Please choose a password" in response.data

    def test_passwordsDontMatch(self, client, app):
        response = client.post("/users", data={
            "username": generate_random_string(),
            "name": "aTester",
            "password": "a",
            "passwordConfirm": "b",
        })

        assert b"Passwords do not match" in response.data

    def test_userNameUnavailable(self, client, app):

        randomUserName = generate_random_string()

        # Initial request to make sure that the user exists
        client.post("/users", data={
            "username": randomUserName,
            "name": "First User",
            "password": "a",
            "passwordConfirm": "a",
        })

        #creating a user logs in as that user, so we need to make sure we are not still logged in
        client.get("/logout")

        #Attempt to create that exact same user name, though the other information may be different
        response = client.post("/users", data={
            "username": randomUserName,
            "name": "Second User",
            "password": "a",
            "passwordConfirm": "a",
        })

        assert b"Username" in response.data
        assert b"is not available" in response.data
