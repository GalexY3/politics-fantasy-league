"""Local account/session boundary for the fictional PFL demo.

Not designed for internet deployment: plain HTTP loopback and no operational
rate limiter, TLS termination, recovery, email verification or audited hosting.
Each account has its own SQLite GAME database, not just a filtered global query.
"""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import time
import uuid
from dataclasses import dataclass
from contextlib import contextmanager
from pathlib import Path

from .product import seed_demo

SESSION_TTL = 8 * 60 * 60
HANDLE = re.compile(r"[a-z][a-z0-9_]{2,23}\Z")
SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS account(
 user_id TEXT PRIMARY KEY,
 handle TEXT NOT NULL UNIQUE,
 password_salt BLOB NOT NULL,
 password_hash BLOB NOT NULL,
 created_at INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS account_session(
 session_hash TEXT PRIMARY KEY,
 user_id TEXT NOT NULL REFERENCES account(user_id) ON DELETE CASCADE,
 csrf_secret TEXT NOT NULL,
 expires_at INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS session_expiry ON account_session(expires_at);
"""


class AccountError(ValueError):
    def __init__(self, code: str, status: int = 400):
        self.code = code
        self.status = status
        super().__init__(code)


@dataclass(frozen=True)
class AccountSession:
    user_id: str
    handle: str
    csrf_secret: str


@contextmanager
def _connect(path: Path):
    db = sqlite3.connect(str(path), timeout=5, isolation_level=None)
    try:
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=5000")
        yield db
    finally:
        db.close()


def init_accounts(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with _connect(path) as db:
        db.executescript(SCHEMA)


def game_path(auth_db: Path, user_id: str) -> Path:
    # Never construct this path from a client-supplied handle or cookie value.
    if not re.fullmatch(r"[a-f0-9]{32}", user_id):
        raise AccountError("INVALID_ACCOUNT_ID", 500)
    return auth_db.parent / "accounts" / (user_id + ".sqlite3")


def _password(password: object) -> bytes:
    if not isinstance(password, str) or not 12 <= len(password) <= 128:
        raise AccountError("PASSWORD_LENGTH_12_TO_128")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in password):
        raise AccountError("BAD_PASSWORD_CHARACTER")
    return password.encode("utf-8")


def _hash_password(password: bytes, salt: bytes) -> bytes:
    return hashlib.scrypt(password, salt=salt, n=16384, r=8, p=1, dklen=32)


def register(path: Path, username: object, password: object) -> str:
    if not isinstance(username, str) or not HANDLE.fullmatch(username.lower()):
        raise AccountError("INVALID_USERNAME")
    handle = username.lower()
    key = _password(password)
    salt = secrets.token_bytes(16)
    digest = _hash_password(key, salt)
    identifier = uuid.uuid4().hex
    with _connect(path) as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute("INSERT INTO account VALUES(?,?,?,?,?)",
                       (identifier, handle, salt, digest, int(time.time())))
            # The game is seeded BEFORE the new account becomes visible.
            seed_demo(game_path(path, identifier))
            db.execute("COMMIT")
        except sqlite3.IntegrityError:
            db.execute("ROLLBACK")
            raise AccountError("USERNAME_TAKEN", 409) from None
        except Exception:
            db.execute("ROLLBACK")
            raise
    return handle


def authenticate(path: Path, username: object, password: object) -> tuple[str, str]:
    if not isinstance(username, str) or not HANDLE.fullmatch(username.lower()):
        raise AccountError("INVALID_CREDENTIALS", 401)
    key = _password(password)
    with _connect(path) as db:
        row = db.execute("SELECT * FROM account WHERE handle=?", (username.lower(),)).fetchone()
    # Return exactly the same public error for unknown users and wrong passwords.
    if row is None:
        _hash_password(key, b"\0" * 16)
        raise AccountError("INVALID_CREDENTIALS", 401)
    good = hmac.compare_digest(_hash_password(key, row["password_salt"]),
                               row["password_hash"])
    if not good:
        raise AccountError("INVALID_CREDENTIALS", 401)
    return row["user_id"], row["handle"]


def login(path: Path, username: object, password: object) -> tuple[str, AccountSession]:
    user_id, handle = authenticate(path, username, password)
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    with _connect(path) as db:
        db.execute("INSERT INTO account_session VALUES(?,?,?,?)",
                   (hashlib.sha256(token.encode()).hexdigest(), user_id, csrf,
                    int(time.time()) + SESSION_TTL))
    return token, AccountSession(user_id, handle, csrf)


def lookup(path: Path, token: str | None) -> AccountSession | None:
    if not isinstance(token, str) or len(token) > 128 or len(token) < 32:
        return None
    with _connect(path) as db:
        row = db.execute("""SELECT a.user_id,a.handle,s.csrf_secret
                            FROM account_session s JOIN account a USING(user_id)
                            WHERE s.session_hash=? AND s.expires_at>?""",
                         (hashlib.sha256(token.encode()).hexdigest(), int(time.time()))).fetchone()
    return AccountSession(**dict(row)) if row else None


def revoke(path: Path, token: str | None) -> None:
    if isinstance(token, str) and 32 <= len(token) <= 128:
        with _connect(path) as db:
            db.execute("DELETE FROM account_session WHERE session_hash=?",
                       (hashlib.sha256(token.encode()).hexdigest(),))


def csrf_matches(session: AccountSession, presented: str | None) -> bool:
    return isinstance(presented, str) and hmac.compare_digest(
        session.csrf_secret, presented)
