from typing import Annotated

from fastapi import APIRouter, Path

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


@users_router.post("/register")
async def register_user_jwt(
    form_data: FormDataDep,
    uow: UOWDep,
) -> UserInfoResponseSchema:
    user = await UsersService().add_user(uow, form_data)
    return user


@token_router.post("/token")
async def get_user_token(
    form_data: FormDataDep,
    uow: UOWDep,
) -> TokenObtainPairSchema:
    token_pair = await AuthService().obtain_tokens_by_credentials(uow, form_data)
    return token_pair


@users_router.get("/users/me")
async def get_user_info(user: UserFromAccessTokenDep) -> UserInfoResponseSchema:
    return user


@token_router.post("/token/refresh")
async def refresh_tokens(
    refresh_token_schema: RefreshTokenSchema,
    uow: UOWDep,
) -> TokenObtainPairSchema:
    token_pair = await AuthService().refresh_tokens(
        uow, refresh_token_schema.refresh_token
    )
    return token_pair


@users_router.post("/users/{user_id}/revoke_tokens")
async def revoke_user_tokens(
    user: UserFromAccessTokenDep,
    uow: UOWDep,
    user_id: Annotated[int, Path(title="id of current user")],
):
    await UsersService().revoke_tokens(uow, user, user_id)
    return {"detail": "Tokens revoked"}
