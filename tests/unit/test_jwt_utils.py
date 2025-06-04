from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException
from pydantic_settings import BaseSettings

from src.config import Settings
from src.schemas.users import TokenPayloadSchema, TokenType
from src.utils.jwt_utils import JwtUtils


@pytest.fixture
def test_settings():
    settings = Settings()

    class TestAuthJwt(BaseSettings):
        secret_key: str = "test_secret_key"
        algorithm: str = "HS256"
        access_token_expire_minutes: int = 15
        refresh_token_expire_minutes: int = 60

    settings.auth_jwt = TestAuthJwt()
    return settings


@pytest.fixture
def jwt_utils(test_settings):
    return JwtUtils(test_settings)


def test_hash_password():
    password = "test_password"
    hashed = JwtUtils.hash_password(password)
    assert isinstance(hashed, str)
    assert hashed != password
    assert JwtUtils.validate_password(password, hashed)


def test_validate_password():
    password = "test_password"
    wrong_password = "wrong_password"
    hashed = JwtUtils.hash_password(password)

    assert JwtUtils.validate_password(password, hashed)
    assert not JwtUtils.validate_password(wrong_password, hashed)


def test_create_token_pair(jwt_utils):
    user_id = 1
    token_version = 1
    token_pair = jwt_utils.create_token_pair(user_id, token_version)

    assert "access_token" in token_pair.model_dump()
    assert "refresh_token" in token_pair.model_dump()

    # Verify access token
    access_payload = jwt_utils.decode_jwt(token_pair.access_token)
    assert access_payload.id == user_id
    assert access_payload.token_type == TokenType.ACCESS
    assert access_payload.token_version == token_version

    # Verify refresh token
    refresh_payload = jwt_utils.decode_jwt(token_pair.refresh_token)
    assert refresh_payload.id == user_id
    assert refresh_payload.token_type == TokenType.REFRESH
    assert refresh_payload.token_version == token_version


def test_decode_jwt_invalid_token(jwt_utils):
    with pytest.raises(HTTPException) as exc_info:
        jwt_utils.decode_jwt("invalid_token")
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


def test_decode_jwt_expired_token(jwt_utils, test_settings):
    payload = {
        "id": 1,
        "token_type": TokenType.ACCESS,
        "token_version": 1,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(
        payload, test_settings.auth_jwt.secret_key, test_settings.auth_jwt.algorithm
    )

    with pytest.raises(HTTPException) as exc_info:
        jwt_utils.decode_jwt(expired_token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token expired"


def test_validate_token_type(jwt_utils):
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = TokenPayloadSchema(
        id=1,
        token_type=TokenType.ACCESS,
        token_version=1,
        exp=int(exp_time.timestamp()),
    )

    # Correct token type
    jwt_utils.validate_token_type(payload, TokenType.ACCESS)

    # Wrong token type
    with pytest.raises(HTTPException) as exc_info:
        jwt_utils.validate_token_type(payload, TokenType.REFRESH)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type"


def test_validate_token_version(jwt_utils):
    exp_time = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = TokenPayloadSchema(
        id=1,
        token_type=TokenType.ACCESS,
        token_version=1,
        exp=int(exp_time.timestamp()),
    )

    # Correct version
    jwt_utils.validate_token_version(payload, 1)

    # Wrong version
    with pytest.raises(HTTPException) as exc_info:
        jwt_utils.validate_token_version(payload, 2)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Token revoked"


def test_token_expiration_times(jwt_utils):
    user_id = 1
    token_version = 1
    token_pair = jwt_utils.create_token_pair(user_id, token_version)

    # Decode tokens to get expiration times
    access_payload = jwt_utils.decode_jwt(token_pair.access_token)
    refresh_payload = jwt_utils.decode_jwt(token_pair.refresh_token)

    now = datetime.now(timezone.utc)
    access_exp = datetime.fromtimestamp(access_payload.exp, timezone.utc)
    refresh_exp = datetime.fromtimestamp(refresh_payload.exp, timezone.utc)

    # Check access token expiration (15 minutes)
    assert abs((access_exp - now).total_seconds() - 15 * 60) < 5

    # Check refresh token expiration (60 minutes)
    assert abs((refresh_exp - now).total_seconds() - 60 * 60) < 5
