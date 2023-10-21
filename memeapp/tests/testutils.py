from memeapp.utils.cryptoutils import hash_password
from memeapp.utils.dbutils import db_execute, get_user_id_by_username
import string
import random

u1 = "alice"
p1 = "alicia"
u2 = "bob"
p2 = "robert"

svg1 = "test1.svg"
svg2 = "test2.svg"


def create_user(username, password, name=None, admin=0):
    name = name if name else username
    pw_hash = hash_password(password)
    db_execute("INSERT INTO users VALUES (?, ?, ?, ?)", p=(username, name, pw_hash.decode("utf-8"), admin))
    return get_user_id_by_username(username)

# A lot of the tests were failing when the database is not deleted between tests,
# so rather than using static names that will collide on the next test run
# this gives us the ability to get a random username to use in tests.
# TODO: ensure the random string is unique to prevent test case failures due to collisions.  This is very unlikely and should be resolved by running the test cases a second time so not something we will worry about
def generate_random_string():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
