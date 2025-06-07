from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class TokenType(str, Enum):
    """Type of authentication token."""

    ACCESS = "access"
    REFRESH = "refresh"


class UserAuthSchema(BaseModel):
    """Schema for user authentication."""

    username: Annotated[
        str,
        Field(
            max_length=255,
            description="User's unique username",
            examples=["john_doe", "alice_smith", "bob123"],
        ),
    ]
    password: Annotated[
        str,
        Field(
            max_length=255,
            description="User's password",
            examples=["SecurePass123!", "StrongPassword456#"],
        ),
    ]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"username": "john_doe", "password": "SecurePass123!"},
                {"username": "alice_smith", "password": "StrongPassword456#"},
            ]
        }
    )


class UserInfoResponseSchema(BaseModel):
    """Schema for user information response."""

    id: int = Field(description="Unique identifier for the user", examples=[1, 2, 3])
    username: Annotated[
        str,
        Field(
            max_length=255,
            description="User's username",
            examples=["john_doe", "alice_smith", "bob123"],
        ),
    ]

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"id": 1, "username": "john_doe"},
                {"id": 2, "username": "alice_smith"},
            ]
        }
    )


class UserSchema(UserInfoResponseSchema, UserAuthSchema):
    """Complete user schema including authentication and token information."""

    token_version: Annotated[
        int, Field(ge=0, description="Version of the user's token", examples=[0, 1, 2])
    ]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "username": "john_doe",
                    "password": "SecurePass123!",
                    "token_version": 1,
                },
                {
                    "id": 2,
                    "username": "alice_smith",
                    "password": "StrongPassword456#",
                    "token_version": 0,
                },
            ]
        },
    )


class AccessTokenSchema(BaseModel):
    """Schema for access token response."""

    access_token: str = Field(
        description="JWT access token for authentication",
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
                }
            ]
        }
    )


class RefreshTokenSchema(BaseModel):
    """Schema for refresh token response."""

    refresh_token: str = Field(
        description="JWT refresh token for obtaining new access tokens",
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZWZyZXNoIn0.kAOUwR3Gk1tB1J9M1zXrXdXoV4SZFPG7nXBgMKKZ8tE"
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZWZyZXNoIn0.kAOUwR3Gk1tB1J9M1zXrXdXoV4SZFPG7nXBgMKKZ8tE"
                }
            ]
        }
    )


class TokenObtainPairSchema(AccessTokenSchema, RefreshTokenSchema):
    """Schema for token pair (access + refresh) response."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZWZyZXNoIn0.kAOUwR3Gk1tB1J9M1zXrXdXoV4SZFPG7nXBgMKKZ8tE",
                }
            ]
        }
    )


class TokenPayloadSchema(BaseModel):
    """Schema for JWT token payload."""

    id: int = Field(description="User ID associated with the token", examples=[1, 2, 3])
    token_version: int = Field(description="Version of the token", examples=[0, 1, 2])
    token_type: TokenType = Field(
        description="Type of token (access or refresh)", examples=["access", "refresh"]
    )
    exp: int = Field(description="Token expiration timestamp", examples=[1712345678])

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "token_version": 1,
                    "token_type": "access",
                    "exp": 1712345678,
                },
                {
                    "id": 1,
                    "token_version": 1,
                    "token_type": "refresh",
                    "exp": 1712345678,
                },
            ]
        },
    )


class TokenSchema(BaseModel):
    """Schema for generic token response."""

    token: str = Field(
        description="JWT token string",
        examples=[
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U"
                }
            ]
        }
    )
