from typing import Annotated

from fastapi import APIRouter, Path, status

from api.v1.dependencies import FormDataDep, UOWDep, UserFromAccessTokenDep
from schemas.users import (
    RefreshTokenSchema,
    TokenObtainPairSchema,
    UserInfoResponseSchema,
)
from services.auth import AuthService
from services.users import UsersService


users_router = APIRouter(
    tags=["Users"],
)

token_router = APIRouter(
    tags=["Token"],
)


@users_router.post(
    "/register",
    response_model=UserInfoResponseSchema,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "User registered successfully",
            "content": {
                "application/json": {"example": {"id": 1, "username": "john_doe"}}
            },
        },
        400: {
            "description": "Username already taken",
            "content": {
                "application/json": {"example": {"detail": "Username already exists"}}
            },
        },
    },
)
async def register_user_jwt(
    form_data: FormDataDep,
    uow: UOWDep,
) -> UserInfoResponseSchema:
    """
    Register a new user.

    Parameters:
    - form_data: User registration data
        - username: Unique username
        - password: User's password

    Returns:
    - UserInfoResponseSchema with user details
    - HTTP 400 if username is already taken
    """
    user = await UsersService().add_user(uow, form_data)
    return user


@token_router.post(
    "/token",
    response_model=TokenObtainPairSchema,
    responses={
        200: {
            "description": "Tokens obtained successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZWZyZXNoIn0.kAOUwR3Gk1tB1J9M1zXrXdXoV4SZFPG7nXBgMKKZ8tE",
                    }
                }
            },
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {"example": {"detail": "Invalid credentials"}}
            },
        },
    },
)
async def get_user_token(
    form_data: FormDataDep,
    uow: UOWDep,
) -> TokenObtainPairSchema:
    """
    Obtain access and refresh tokens using username and password.

    Parameters:
    - form_data: User credentials
        - username: User's username
        - password: User's password

    Returns:
    - TokenObtainPairSchema containing access and refresh tokens
    - HTTP 401 if credentials are invalid
    """
    token_pair = await AuthService().obtain_tokens_by_credentials(uow, form_data)
    return token_pair


@users_router.get(
    "/users/me",
    response_model=UserInfoResponseSchema,
    responses={
        200: {
            "description": "Current user information",
            "content": {
                "application/json": {"example": {"id": 1, "username": "john_doe"}}
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def get_user_info(user: UserFromAccessTokenDep) -> UserInfoResponseSchema:
    """
    Get current user information.

    Returns:
    - UserInfoResponseSchema with user details
    - HTTP 401 if access token is invalid or expired
    """
    return user


@token_router.post(
    "/token/refresh",
    response_model=TokenObtainPairSchema,
    responses={
        200: {
            "description": "Tokens refreshed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J3jVmNHl0w5N_XgL0n3I9PlFUP0THsR8U",
                        "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJyZWZyZXNoIn0.kAOUwR3Gk1tB1J9M1zXrXdXoV4SZFPG7nXBgMKKZ8tE",
                    }
                }
            },
        },
        401: {
            "description": "Invalid refresh token",
            "content": {
                "application/json": {"example": {"detail": "Invalid refresh token"}}
            },
        },
    },
)
async def refresh_tokens(
    refresh_token_schema: RefreshTokenSchema,
    uow: UOWDep,
) -> TokenObtainPairSchema:
    """
    Get new access and refresh tokens using a refresh token.

    Parameters:
    - refresh_token_schema: Current refresh token
        - refresh_token: Valid refresh token string

    Returns:
    - TokenObtainPairSchema containing new access and refresh tokens
    - HTTP 401 if refresh token is invalid or expired
    """
    token_pair = await AuthService().refresh_tokens(
        uow, refresh_token_schema.refresh_token
    )
    return token_pair


@users_router.post(
    "/users/{user_id}/revoke_tokens",
    responses={
        200: {
            "description": "Tokens revoked successfully",
            "content": {"application/json": {"example": {"detail": "Tokens revoked"}}},
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "This action can only be performed on your own account"
                    }
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def revoke_user_tokens(
    user: UserFromAccessTokenDep,
    uow: UOWDep,
    user_id: Annotated[int, Path(title="id of current user")],
):
    """
    Revoke all tokens for a user by incrementing their token version.
    This invalidates all existing access and refresh tokens.

    Parameters:
    - user_id: ID of the user whose tokens should be revoked
    - user: Current authenticated user (must match user_id)

    Returns:
    - Success message if tokens were revoked
    - HTTP 403 if user_id doesn't match authenticated user
    """
    await UsersService().revoke_tokens(uow, user, user_id)
    return {"detail": "Tokens revoked"}
