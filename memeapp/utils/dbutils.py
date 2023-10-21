import sqlite3
import os

from flask import current_app, g


def get_db():
    if "db" not in g:
        db_name = current_app.config["DATABASE"]
        g.db = sqlite3.connect(db_name)
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialize_db():
    db = get_db()
    with current_app.open_resource("resources/schema.sql") as f:
        db.executescript(f.read().decode("utf8"))


def db_query(query, p=(), one=False):
    db = get_db()
    cur = db.execute(query, p)
    if one:
        results = cur.fetchone()
    else:
        results = cur.fetchall()
    cur.close()
    return results


def db_execute(query, p=()):
    db = get_db()
    cur = db.execute(query, p)
    db.commit()
    rowid = cur.lastrowid
    cur.close()
    return rowid


def init_app(app):
    with app.app_context():
        if not os.path.exists(app.config["DATABASE"]) or app.config['TESTING'] is True:
            initialize_db()
    app.teardown_appcontext(close_db)


def get_user_id_by_username(username: str):
    if username:
        result = db_query("SELECT rowid FROM users WHERE username=?", (username,), one=True)
        if result:
            return result[0]
    return None
