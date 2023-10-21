import io
from memeapp.tests.testutils import create_user, generate_random_string, u1, p1, u2, p2
from memeapp.utils import cryptoutils
from memeapp.utils.dbutils import db_query, get_user_id_by_username

class TestProfile:
    #We are only testing edit specific tests here.  All of the validation tests for user registration could also be replicated, but for edit

    def test_view_profile(self, client, app):
        #We create a local user since we are getting bleed through from other test cases which messed up the meme owned and comment count
        user1 = generate_random_string();
        with app.app_context():
            create_user(user1, user1)

        client.post("/login", data={"username": user1, "password": user1})

        #Meme 1
        d = {'file': (io.BytesIO(b"<svg>File1</svg>"), "test_meme_upload_download.svg"),
             'name': "File 1"}
        response = client.post("/upload", data=d)
        m1id = response.location.split("/")[-1]

        d = {"title": "Too funny", "body": "I like this meme"}
        client.post(f"/memes/{m1id}/comments", json=d)

        d = {"title": "dank", "body": "Very good"}
        client.post(f"/memes/{m1id}/comments", json=d)

        #Meme 2
        d = {'file': (io.BytesIO(b"<svg>File2</svg>"), "test_meme_upload_download.svg"),
             'name': "File 2"}
        response = client.post("/upload", data=d)
        m2id = response.location.split("/")[-1]

        d = {"title": "Boring", "body": "Try again"}
        client.post(f"/memes/{m2id}/comments", json=d)

        response = client.get("/profile")

        print(response.data)

        assert bytes(f"<div id=\"name\">{user1}</div>", 'utf-8') in response.data
        assert bytes(f"<div id=\"memeCount\">2</div>", encoding='utf-8') in response.data
        assert bytes(f"<div id=\"commentCount\">3</div>", encoding='utf-8') in response.data

    def test_view_own_profile_edit_link(self, client, app):
        client.post("/login", data={"username": u1, "password": p1})

        response = client.get("/profile")
        assert bytes(f"Edit", 'utf-8') in response.data

    def test_view_other_profile_edit_link(self, client, app):
        client.post("/login", data={"username": u1, "password": p1})

        with app.app_context():
            user2id = get_user_id_by_username(u2)

        response = client.get(f"/users/{user2id}")
        assert bytes(f"Edit", 'utf-8') not in response.data

    def test_get_user(self, client, app):
        # authenticate as first user
        client.post("/login", data={"username": u1, "password": p1})

        # get my user
        with app.app_context():
            user1id = get_user_id_by_username(u1)
        response = client.get(f"/users/{user1id}")
        #assert response.json["username"] == u1
        assert bytes(f"<div id=\"name\">{u1}</div>", 'utf-8') in response.data

        # get someone else's username
        with app.app_context():
            user2id = get_user_id_by_username(u2)
        response = client.get(f"/users/{user2id}")
        #assert response.json["username"] == u2
        assert bytes(f"<div id=\"name\">{u2}</div>", 'utf-8') in response.data

    def test_no_current_password(self, client, app):
        user1 = generate_random_string();

        newName = 'Something new'
        oldName = 'Something old'

        with app.app_context():
            user_id = create_user(user1, user1, oldName)
        
        client.post("/login", data={"username": user1, "password": user1})
        
        response = client.get("/profile")

        assert bytes(f"<div id=\"name\">{oldName}</div>", 'utf-8') in response.data

        response = client.post("/users", data={
            "name": newName,
        })

        assert b"Please enter your current password" in response.data

        with app.app_context():
            result = db_query("SELECT name FROM users WHERE username=?", (user1,), one=True)
            print("Result to verify",result)
            assert result
            assert result[0] == oldName

    def test_wrong_current_password(self, client, app):
        user1 = generate_random_string();

        newName = 'Something new'
        oldName = 'Something old'

        with app.app_context():
            user_id = create_user(user1, user1, oldName)
        
        client.post("/login", data={"username": user1, "password": user1})
        
        response = client.get("/profile")

        assert bytes(f"<div id=\"name\">{oldName}</div>", 'utf-8') in response.data

        response = client.post("/users", data={
            "name": newName,
            "currentPassword": "ThePasswordShouldBeAnythingButThis1!"
        })

        assert b"Current password does not match what is on file." in response.data

        with app.app_context():
            result = db_query("SELECT name FROM users WHERE username=?", (user1,), one=True)
            print("Result to verify",result)
            assert result
            assert result[0] == oldName

    def test_change_own_name(self, client, app):
        user1 = generate_random_string();

        newName = 'Something new'
        oldName = 'Something old'

        with app.app_context():
            user_id = create_user(user1, user1, oldName)
        
        client.post("/login", data={"username": user1, "password": user1})

        response = client.get("/profile")

        assert bytes(f"<div id=\"name\">{oldName}</div>", 'utf-8') in response.data

        response = client.post("/users", data={
            "name": newName,
            "currentPassword": user1,
        })

        assert b"User updated" in response.data

        with app.app_context():
            result = db_query("SELECT name FROM users WHERE username=?", (user1,), one=True)
            assert result
            assert result[0] == newName

    def test_change_own_password(self, client, app):
        user1 = generate_random_string();

        with app.app_context():
            user_id = create_user(user1, user1, user1)
        
        client.post("/login", data={"username": user1, "password": user1})

        response = client.get("/profile")

        assert bytes(f"<div id=\"name\">{user1}</div>", 'utf-8') in response.data

        newPassword = "secret"

        response = client.post("/users", data={
            "name": user1, #the way things are written now name is always required, even if they want to only change thier password and not their name
            "password": newPassword,
            "passwordConfirm": newPassword,
            "currentPassword": user1,
        })

        print("response", response.data)

        assert response.status_code == 200
        assert b"User updated" in response.data

        with app.app_context():
            password_hash = db_query(f"SELECT password_hash FROM users WHERE username='{user1}'", one=True)

        assert password_hash
        assert cryptoutils.check_password(newPassword, password_hash[0])
