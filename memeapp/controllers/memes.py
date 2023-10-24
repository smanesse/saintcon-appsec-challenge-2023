from flask import g, render_template, request, redirect, Response, send_file, Blueprint, current_app, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json

from memeapp.utils.dbutils import db_query, db_execute, get_user_id_by_username
from memeapp.controllers.users import login_required
from memeapp.model import Meme
import os

bp = Blueprint("memes", __name__)


def get_driver():
    """Sets chrome options for Selenium.
    Chrome options for headless browser is enabled.
    See https://nander.cc/using-selenium-within-a-docker-container
    """
    service = Service(executable_path="/usr/bin/chromedriver")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.experimental_options["prefs"] = chrome_prefs
    # chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return webdriver.Chrome(options=chrome_options, service=service)


def save_meme(file, name):
    ext = file.filename.rsplit(".")[-1]
    if "." in file.filename and len(ext) < 6 and not name.endswith(ext):
        name += "." + ext
    file_id = db_execute("INSERT INTO memes(name, owner) VALUES (?, ?)", (name, g.user.id))
    path = os.path.join(current_app.config['UPLOAD_DIRECTORY'], name)
    if not os.path.exists(path):
        file.save(path)
    return file_id


@bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload_meme():
    if request.method == "POST":
        if 'file' not in request.files or 'name' not in request.form:
            return redirect("/upload")
        file = request.files['file']
        if file.filename == '':
            return redirect("/upload")
        if file:
            name = request.form.get("name")
            file_id = save_meme(file, name)
            return redirect(f"/memes/{file_id}")
        else:
            return redirect("/upload")

    return render_template("upload.html", user=g.user)


@bp.route("/import", methods=["POST"])
@login_required
def import_meme():
    url = request.form.get("url")
    name = request.form.get("name")
    if not name.endswith(".png"):
        name = name + ".png"
    driver = get_driver()
    driver.get(url)
    file_id = db_execute("INSERT INTO memes(name, owner) VALUES (?, ?)", (name, g.user.id))
    driver.save_screenshot(os.path.join(current_app.config['UPLOAD_DIRECTORY'], name))
    return redirect(f"/memes/{file_id}")


@bp.route("/memes/<meme_id>/view", methods=["GET"])
@login_required
def get_meme(meme_id):
    def get_mimetype(fname):
        if fname.endswith(".png"):
            return "image/png"
        elif fname.endswith(".jpeg") or fname.endswith(".jpg"):
            return "image/jpeg"
        else:
            return "image/svg+xml"

    result = db_query("SELECT name, owner FROM memes WHERE rowid=?", (meme_id,), one=True)
    if not result:
        return Response("Not Found", status=404)
    name, u = result
    shared = map(lambda x: x[0], db_query("SELECT user FROM meme_shares WHERE meme=?", (meme_id,), one=False))
    valid_users = {u, *shared}
    if u not in valid_users:
        return Response("Not Found", status=404)
    return send_file(os.path.join(current_app.config['UPLOAD_DIRECTORY'], name),
                     mimetype=get_mimetype(name))


@bp.route("/memes/<meme_id>", methods=["GET"])
@login_required
def view_meme(meme_id):
    result = db_query("SELECT name, owner FROM memes WHERE rowid=?", (meme_id,), one=True)
    if not result:
        return Response("Not Found", status=404)
    name, u = result
    shared = map(lambda x: x[0], db_query("SELECT user FROM meme_shares WHERE meme=?", (meme_id,), one=False))
    valid_users = {u, *shared}
    if g.user.id not in valid_users:
        return Response("Not Found", status=404)
    return render_template("meme.html", meme=Meme(id=meme_id, name=name, owner=g.user), user=g.user)


@bp.route("/memes/<meme_id>/shares", methods=["POST"])
@login_required
def share_meme(meme_id):
    result = db_query("SELECT name, owner FROM memes WHERE rowid=?", (meme_id,), one=True)
    if not result:
        return Response("Not Found", status=404)
    name, owner_id = result
    if owner_id != g.user.id:
        return Response("Not Found", status=404)
    data = json.loads(request.data.decode("UTF-8"))
    if 'username' not in data:
        return Response("Bad Request", status=400)
    username = data['username']
    user_id = get_user_id_by_username(username)
    if not user_id:
        return Response("Bad Request", status=400)
    db_execute("INSERT INTO meme_shares VALUES (?, ?)", (user_id, meme_id))
    return Response("Created", status=201)


@bp.route("/memes/<meme_id>/comments", methods=["POST", "GET"])
@login_required
def comments(meme_id):
    result = db_query("SELECT name, owner FROM memes WHERE rowid=?", (meme_id,), one=True)
    if not result:
        return Response("Not Found", status=404)
    name, u = result
    shared = map(lambda x: x[0], db_query("SELECT user FROM meme_shares WHERE meme=?", (meme_id,), one=False))
    valid_users = {u, *shared}
    if g.user.id not in valid_users:
        return Response("Not Found", status=404)

    if request.method == "GET":
        meme_comments = db_query("SELECT title, author, body FROM comments WHERE meme=? ORDER BY rowid DESC",
                                 (meme_id,))
        user_ids_in_memes = (",".join(list(set([str(x[1]) for x in meme_comments]))))

        sql = f"SELECT rowid, username FROM users WHERE rowid in ({user_ids_in_memes})"
        usernames = db_query(sql)
        usernames = {x[0]: x[1] for x in usernames}

        return jsonify(
            {"comments": list(
                map(lambda x: {
                    "title": x[0],
                    "author": {"id": str(x[1]),
                               "username": usernames[x[1]]
                               },
                    "body": x[2]},
                    meme_comments))})
    else:
        data = request.json
        author = g.user.id
        title = data["title"][:500]
        body = data["body"][:5000]
        row_id = db_execute("INSERT INTO comments(title, author, meme, body) VALUES(?,?,?,?)",
                            (title, author, meme_id, body))
        return Response(str(row_id), status=201)
