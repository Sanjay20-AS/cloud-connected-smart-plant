from datetime import datetime, timedelta, timezone
import hashlib
import hmac

import jwt

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .config import settings


ALGORITHM = "HS256"


# Tells FastAPI/Swagger that this API uses Bearer authentication
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        b"smart-plant-demo",
        120_000
    ).hex()


def verify_password(password: str, expected_plaintext: str) -> bool:
    return hmac.compare_digest(
        hash_password(password),
        hash_password(expected_plaintext)
    )


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=settings.token_expire_minutes),
    }

    return jwt.encode(
        payload,
        settings.jwt_secret,
        algorithm=ALGORITHM
    )


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    if credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )

    token = credentials.credentials

    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[ALGORITHM]
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )


def require_device(
    x_device_key: str | None = Header(default=None)
):
    if not x_device_key:
        raise HTTPException(
            status_code=401,
            detail="Device API key missing"
        )

    if not hmac.compare_digest(
        x_device_key,
        settings.device_api_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid device key"
        )

    return True