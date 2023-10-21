import io
from memeapp.utils.dbutils import db_query
from memeapp.tests.testutils import u1, p1, u2, p2


class TestComments:
    def test_add_comment_one_user(self, client, app):
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>test_meme_upload_download</svg>"), "test_meme_upload_download.svg"),
             'name': "test_meme_upload_download.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        title = "mytitle1~!@#$%^&*()_+-={}|[]\\:\";'<>?,./'"
        body = "mybody1~!@#$%^&*()_+-={}|[]\\:\";'<>?,./'"
        d = {"title": title, "body": body}
        client.post(f"memes/{mid}/comments", json=d)
        with app.app_context():
            count = db_query("SELECT COUNT(*) FROM comments WHERE author=? AND meme=? AND title=? AND body=?",
                             (1, mid, title, body), one=True)
        assert count[0] == 1

    def test_get_comments_one_user(self, client):
        client.post("/login", data={"username": u1, "password": p1})
        d = {'file': (io.BytesIO(b"<svg>test_meme_upload_download</svg>"), "test_meme_upload_download.svg"),
             'name': "test_meme_upload_download.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]
        title = "mytitle2~!@#$%^&*()_+-={}|[]\\:\";'<>?,./'"
        body = "mybody2~!@#$%^&*()_+-={}|[]\\:\";'<>?,./'"
        d = {"title": title, "body": body}
        client.post(f"/memes/{mid}/comments", json=d)
        response = client.get(f"/memes/{mid}/comments").json
        assert response["comments"][0]["title"] == title
        assert response["comments"][0]["body"] == body
        assert response["comments"][0]["author"]["id"] == '1'
        assert response["comments"][0]["author"]["username"] == u1

    def test_get_comments_two_users(self, client):
        #u1 login
        client.post("/login", data={"username": u1, "password": p1})

        #u1 upload
        d = {'file': (io.BytesIO(b"<svg>test_meme_upload_download</svg>"), "test_meme_upload_download.svg"),
             'name': "test_meme_upload_download.svg"}
        response = client.post("/upload", data=d)
        mid = response.location.split("/")[-1]

        #u1 comment
        title1 = "foo"
        body1 = "bar"
        d = {"title": title1, "body": body1}
        client.post(f"/memes/{mid}/comments", json=d)

        #u1 shares with u2
        response = client.post(f"/memes/{mid}/shares", json={"username": u2})

        client.post("/logout")

        #u2 login
        client.post("/login", data={"username": u2, "password": p2})

        #u2 comment
        title2 = "Hello"
        body2 = "World"
        d = {"title": title2, "body": body2}
        client.post(f"/memes/{mid}/comments", json=d)

        #load comments
        response = client.get(f"/memes/{mid}/comments").json

        print("Two user comment response:", response)

        #If we add an explicit ordering in SQL these values could change
        user1CommentIndex = 1
        user2CommentIndex = 0

        assert response["comments"][user1CommentIndex]["title"] == title1
        assert response["comments"][user1CommentIndex]["body"] == body1
        assert response["comments"][user1CommentIndex]["author"]["id"] == '1'
        assert response["comments"][user1CommentIndex]["author"]["username"] == u1

        assert response["comments"][user2CommentIndex]["title"] == title2
        assert response["comments"][user2CommentIndex]["body"] == body2
        assert response["comments"][user2CommentIndex]["author"]["id"] == '2'
        assert response["comments"][user2CommentIndex]["author"]["username"] == u2