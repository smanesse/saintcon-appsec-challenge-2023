import pytest
from memeapp.conf.constants import DB_NAME, UPLOAD_DIR_NAME
from memeapp.utils.cryptoutils import hash_password
from memeapp.app import create_app
from memeapp.utils.dbutils import db_execute
from memeapp.tests.testutils import u1, u2, p1, p2

testDB_name = "test_" + DB_NAME
upload_dir = "test_" + UPLOAD_DIR_NAME


def load_test_data(app):
    # users
    db_execute("INSERT INTO users VALUES (?, ?, ?, ?)", p=(u1, u1, hash_password(p1).decode("utf-8"), 0))
    db_execute("INSERT INTO users VALUES (?, ?, ?, ?)", p=(u2, u2, hash_password(p2).decode("utf-8"), 0))


@pytest.fixture(scope="session")
def app():
    app = create_app({
        "TESTING": True,
        "DATABASE": testDB_name,
        "UPLOAD_DIRECTORY": upload_dir,
    })
    with app.app_context():
        load_test_data(app)
    yield app


@pytest.fixture(scope="function")
def client(app):
    client = app.test_client()
    #make sure the user is 100% logged out before each test case
    client.get("/logout")
    return client


@pytest.fixture(scope="session")
def runner(app):
    return app.test_cli_runner()
