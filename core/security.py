from datetime import datetime, timezone, timedelta

import jwt
from jwt.exceptions import InvalidTokenError
import argon2

from core.settings import settings
from schemas.auth import TokenData


ph = argon2.PasswordHasher()


def hash_password(password: str) -> str:
    return ph.hash(password)


def verify_password(hash: str, password: str) -> bool:
    try:
        ph.verify(hash, password)
    except (
        argon2.exceptions.VerifyMismatchError,
        argon2.exceptions.VerificationError,
        argon2.exceptions.InvalidHashError
    ):
        return False
    else:
        return True


class InvalidCredentials(Exception):
    pass


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_key,
            algorithms=[settings.jwt_algo],
        )
    except InvalidTokenError as e:
        raise InvalidCredentials from e

    username = payload.get("sub")
    if username is None:
        raise InvalidCredentials

    return TokenData(username=username)


def encode_token(username: str) -> str:
    expire = (
        datetime.now(timezone.utc)
        + timedelta(minutes=settings.jwt_minutes)
    )
    return jwt.encode(
        {
            "sub": username,
            "exp": expire
        },
        settings.jwt_key,
        algorithm=settings.jwt_algo
    )
