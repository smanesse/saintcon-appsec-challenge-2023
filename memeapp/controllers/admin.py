import os

from flask import Blueprint, redirect, render_template, g, request

not_settings = set(dir())
from memeapp.conf.config import *

settings = set(dir()) - not_settings - {"not_settings"}

bp = Blueprint("admin", __name__)


@bp.route("/admin", methods=["GET"])
def index():
    if "selenium-nolocalhost" in request.headers.get("user-agent"):
        return redirect("/home")
    if request.remote_addr == "127.0.0.1" or (g.user and g.user.is_admin):
        return render_template("admin.html", environ=os.environ, user=g.user,
                               settings={name: eval(name) for name in settings if not name.startswith("__")})
    return redirect("/home")
