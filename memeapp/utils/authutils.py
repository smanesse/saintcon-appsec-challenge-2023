from flask import redirect, g, url_for, current_app
import functools
from memeapp.utils import cryptoutils
from memeapp.conf import constants


def login_required(f):
    @functools.wraps(f)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("users.login"))
        return f(**kwargs)

    return wrapped_view


def set_session_token(user_id, response):
    session_token = cryptoutils.get_session_token(user_id)
    response.set_cookie(constants.SESSION_TOKEN_NAME, session_token, secure=(not current_app.config["DEBUG"]),
                        httponly=True,
                        samesite="Lax")


def clear_session_token(response):
    response.delete_cookie(constants.SESSION_TOKEN_NAME)
