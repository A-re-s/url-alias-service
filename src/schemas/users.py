from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class UserAuthSchema(BaseModel):
    username: Annotated[str, Field(max_length=255)]
    password: Annotated[str, Field(max_length=255)]

    model_config = {
        "json_schema_extra": {
            "examples": [{"username": "user123", "password": "securepassword"}]
        }
    }


class UserInfoResponseSchema(BaseModel):
    id: int
    username: Annotated[str, Field(max_length=255)]

    model_config = {
        "json_schema_extra": {"examples": [{"id": 1, "username": "user123"}]}
    }


class UserSchema(UserInfoResponseSchema, UserAuthSchema):
    token_version: Annotated[int, Field(ge=0)]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "user123",
                    "password": "securepassword",
                    "token_version": 1,
                }
            ]
        },
    )


class AccessTokenSchema(BaseModel):
    access_token: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]
        }
    }


class RefreshTokenSchema(BaseModel):
    refresh_token: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4="}]
        }
    }


class TokenObtainPairSchema(AccessTokenSchema, RefreshTokenSchema):
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2ggdG9rZW4=",
                }
            ]
        }
    }


class TokenPayloadSchema(BaseModel):
    id: int
    token_version: int
    token_type: TokenType
    exp: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "token_version": 1,
                    "token_type": "access",
                    "exp": 1712345678,
                }
            ]
        },
    )


class TokenSchema(BaseModel):
    token: str

    model_config = {
        "json_schema_extra": {
            "examples": [{"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}]
        }
    }
