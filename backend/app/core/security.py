"""Security helpers: password hashing + signed token (JWT-like) + auth dependencies."""
import hashlib
import hmac
import secrets
from base64 import b64decode, b64encode
from datetime import datetime, timedelta, timezone
from json import dumps, loads

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

_bearer = HTTPBearer(auto_error=False)

PEPPER = settings.secret_key


def hash_password(password: str, salt: str | None = None) -> str:
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}${b64encode(digest).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return hmac.compare_digest(hash_password(password, salt), stored)


def _b64url(data: bytes) -> str:
    return b64encode(data).rstrip(b"=").decode()


def _b64url_decode(data: str) -> bytes:
    return b64decode(data + "=" * (-len(data) % 4))


def create_token(subject: str, role: str, token_type: str = "access", expire_minutes: int | None = None) -> str:
    minutes = expire_minutes if expire_minutes is not None else settings.access_token_expire_minutes
    if token_type == "refresh":
        minutes = settings.refresh_token_expire_days * 24 * 60
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "role": role,
        "type": token_type,
        "jti": secrets.token_hex(8),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
        "iat": int(now.timestamp()),
    }
    header = _b64url(dumps({"alg": "HS256", "typ": "JWT"}).encode())
    body = _b64url(dumps(payload).encode())
    signing_input = f"{header}.{body}"
    signature = _b64url(hmac.new(PEPPER.encode(), signing_input.encode(), hashlib.sha256).digest())
    return f"{signing_input}.{signature}"


def decode_token(token: str) -> dict:
    try:
        header, body, signature = token.split(".")
        expected = _b64url(hmac.new(PEPPER.encode(), f"{header}.{body}".encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(signature, expected):
            raise ValueError("bad signature")
        payload = loads(_b64url_decode(body).decode())
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        if exp < datetime.now(timezone.utc):
            raise ValueError("expired")
        return payload
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc


def create_access_token(user) -> str:
    return create_token(str(user["id"]), str(user.get("role", "")))


def create_refresh_token(user) -> str:
    return create_token(str(user["id"]), str(user.get("role", "")), token_type="refresh")


def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> dict:
    token = get_token(request, credentials)
    payload = decode_token(token)
    from app.db import get
    user = get("users", payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def get_token(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    if credentials and credentials.scheme.lower() == "bearer":
        return credentials.credentials
    cookie = request.cookies.get("access_token")
    if cookie:
        return cookie
    raise HTTPException(status_code=401, detail="Not authenticated")