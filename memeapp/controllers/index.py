from flask import Blueprint, redirect, render_template, g
from memeapp.controllers.users import get_user

from memeapp.utils.authutils import login_required
from memeapp.utils.dbutils import db_query
from memeapp.model import Meme, User

bp = Blueprint("index", __name__)


@bp.route("/", methods=["GET"])
def index():
    if g.user:
        return redirect("/home")
    return render_template("authenticate.html", errors=None, warnings=None, infos=None, successes=None)


@bp.route("/home", methods=["GET"])
@login_required
def home():
    memes = db_query("SELECT rowid, name FROM memes WHERE owner=?", (g.user.id,))
    memes = [Meme(*x, owner=g.user) for x in memes]
    return render_template("home.html", memes=memes, user=g.user, errors=None, warnings=None, infos=None,
                           successes=None)


@bp.route("/shared", methods=["GET"])
@login_required
def shared():
    memes = db_query(
        """SELECT memes.rowid, memes.name, users.rowid, users.username, users.name AS memeid
                 FROM memes
                 INNER JOIN meme_shares
                 ON meme_shares.meme = memes.rowid
                 INNER JOIN users
                 ON memes.owner = users.rowid
                 WHERE meme_shares.user = ? AND memes.owner != ?""",
        (g.user.id, g.user.id))

    shared_memes = [Meme(id=x[0], name=x[1], owner=User(id=x[2], username=x[3], name=x[4], is_admin=0)) for x in memes]
    return render_template("shared.html", memes=shared_memes, user=g.user)


@bp.route("/profile", methods=["GET"])
def viewMyProfile():
    if not g.user:
        return redirect("/")
    return get_user(user_id=g.user.id)

@bp.route("/editMyProfile", methods=["GET"])
def editProfile():
    if not g.user:
        print("No user currently logged in")
        return redirect("/")
    return render_template("profile/editProfile.html", user=g.user)
