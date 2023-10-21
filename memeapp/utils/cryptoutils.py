import bcrypt
from hashlib import sha256
from datetime import datetime, timedelta
from memeapp.conf import config
import pickle
import base64
from dataclasses import dataclass

from memeapp.conf.constants import SESSION_TOKEN_NAME


@dataclass
class Session:
    timestamp: int
    user_id: int
    signature: str


def hash_password(raw_password: str):
    if not raw_password:
        return
    salt = bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS)
    s = salt + config.PEPPER
    return bcrypt.hashpw(raw_password.encode("utf-8"), s)


def check_password(raw_password: str, password_hash: str) -> bool:
    if not raw_password:
        return False
    if not password_hash:
        return False
    return bcrypt.checkpw(raw_password.encode("utf-8"), password_hash.encode("utf-8"))


def sign(val: str) -> str:
    return sha256((val + config.SECRET_KEY).encode("utf-8")).hexdigest()


def get_session_token(user_id: int, ts: int = int(datetime.utcnow().timestamp())) -> str:
    assertion = f"{user_id}-{ts}"
    signature = sign(assertion)
    session = Session(ts, user_id, signature)
    return base64.b64encode(pickle.dumps(session)).decode().strip()


def get_session_from_token(token) -> Session:
    decoded = base64.b64decode(token.encode())
    return pickle.loads(decoded)


def verify_session_token(request) -> bool:
    token = request.cookies.get(SESSION_TOKEN_NAME)
    if not token:
        token = request.headers.get("Authorization")
    if not token:
        return False
    session = get_session_from_token(token)
    if not session:
        return False
    assertion = f"{session.user_id}-{session.timestamp}"
    is_valid_signature = sign(assertion) == session.signature
    expired = datetime.now() - timedelta(hours=config.SESSION_EXPIRY) >= datetime.fromtimestamp(
        int(float(session.timestamp)))
    return is_valid_signature and not expired


def get_verified_user_id_from_request(request) -> int:
    # fail if the session token isn't valid
    if not verify_session_token(request):
        return -1

    token = request.headers.get("Authorization")
    if not token:
        token = request.cookies.get(SESSION_TOKEN_NAME)

    user_id = get_session_from_token(token).user_id

    return int(user_id)
