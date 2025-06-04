from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi import HTTPException, status
from pydantic import ValidationError

from config import Settings, get_settings
from schemas.users import (
    AccessTokenSchema,
    RefreshTokenSchema,
    TokenObtainPairSchema,
    TokenPayloadSchema,
    TokenType,
)


class JwtUtils:
    def __init__(self, settings: Settings) -> None:
        self.__settings = settings
        self.__algorithm = settings.auth_jwt.algorithm
        self.__secret_key = settings.auth_jwt.secret_key

    def __encode_jwt(self, payload: dict[str, Any], expire_time_delta: int) -> str:
        to_encode = payload.copy()
        to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
            minutes=expire_time_delta
        )
        encoded = jwt.encode(to_encode, self.__secret_key, self.__algorithm)
        return encoded

    def __create_token(self, user_id: int, token_type: str, token_version: int) -> str:
        token_payload = {
            "id": user_id,
            "token_type": token_type,
            "token_version": token_version,
        }
        expire_time_delta = (
            self.__settings.auth_jwt.access_token_expire_minutes
            if token_type == TokenType.ACCESS
            else self.__settings.auth_jwt.refresh_token_expire_minutes
        )
        return self.__encode_jwt(token_payload, expire_time_delta=expire_time_delta)

    def __create_access_token(
        self, user_id: int, token_version: int
    ) -> AccessTokenSchema:
        token = self.__create_token(user_id, TokenType.ACCESS, token_version)
        return AccessTokenSchema(access_token=token)

    def __create_refresh_token(
        self, user_id: int, token_version: int
    ) -> RefreshTokenSchema:
        token = self.__create_token(user_id, TokenType.REFRESH, token_version)
        return RefreshTokenSchema(refresh_token=token)

    def create_token_pair(
        self, user_id: int, token_version: int
    ) -> TokenObtainPairSchema:
        access_token = self.__create_access_token(user_id, token_version).access_token
        refresh_token = self.__create_refresh_token(
            user_id, token_version
        ).refresh_token
        return TokenObtainPairSchema(
            access_token=access_token, refresh_token=refresh_token
        )

    def decode_jwt(
        self,
        token: str,
    ) -> TokenPayloadSchema:
        try:
            decoded = jwt.decode(
                token, self.__secret_key, algorithms=[self.__algorithm]
            )
            return TokenPayloadSchema(**decoded)
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except (jwt.DecodeError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    def validate_token_type(
        self,
        token_payload: TokenPayloadSchema,
        expected_token_type: str,
    ):
        if token_payload.token_type != expected_token_type:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )

    def validate_token_version(
        self,
        token_payload: TokenPayloadSchema,
        user_token_version: int,
    ):
        if token_payload.token_version != user_token_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked"
            )

    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    @staticmethod
    def validate_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))


jwt_service = JwtUtils(get_settings())
