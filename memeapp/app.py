import os

from flask import Flask, request, g
from memeapp.utils import dbutils, cryptoutils
from memeapp.conf.constants import DB_NAME, UPLOAD_DIR_NAME
from memeapp.model import User


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping({
        "UPLOAD_DIRECTORY": os.path.join(app.instance_path, UPLOAD_DIR_NAME),
        "DATABASE": os.path.join(app.instance_path, DB_NAME),
    })

    if test_config is None:
        # load the instance config, if it exists, when not running tests
        app.config.from_pyfile("conf/config.py", silent=True)
    else:
        test_config["DATABASE"] = os.path.join(app.instance_path, test_config["DATABASE"])
        test_config["UPLOAD_DIRECTORY"] = os.path.join(app.instance_path, test_config["UPLOAD_DIRECTORY"])
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    try:
        os.makedirs(app.config["UPLOAD_DIRECTORY"])
    except OSError:
        pass

    dbutils.init_app(app)

    @app.before_request
    def with_user():
        user_id = cryptoutils.get_verified_user_id_from_request(request)
        if user_id > 0:
            result = dbutils.db_query("SELECT name, username, is_admin FROM users WHERE rowid=?", (user_id,), one=True)
            if result:
                name, username, is_admin = result
                g.user = User(user_id, username, name, is_admin)
            else:
                g.user = None
        else:
            g.user = None

    from memeapp.controllers import index, users, memes, admin
    app.register_blueprint(index.bp)
    app.register_blueprint(users.bp)
    app.register_blueprint(memes.bp)
    app.register_blueprint(admin.bp)

    return app
