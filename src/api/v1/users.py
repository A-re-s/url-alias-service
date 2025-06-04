from typing import Annotated

from fastapi import APIRouter, Depends, Path
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from api.v1.dependencies import UOWDep
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


@users_router.post("/register")
async def register_user_jwt(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: UOWDep,
) -> UserInfoResponseSchema:
    user = await UsersService().add_user(uow, form_data)
    return user


@token_router.post("/token")
async def get_user_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    uow: UOWDep,
) -> TokenObtainPairSchema:
    token_pair = await AuthService().obtain_tokens_by_credentials(uow, form_data)
    return token_pair


@users_router.get("/users/me")
async def get_user_info(
    access_token: Annotated[str, Depends(oauth2_scheme)],
    uow: UOWDep,
) -> UserInfoResponseSchema:
    user = await AuthService().get_user_by_access_token(uow, access_token)
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
    access_token: Annotated[str, Depends(oauth2_scheme)],
    uow: UOWDep,
    user_id: Annotated[int, Path(title="id of current user")],
):
    user = await AuthService().get_user_by_access_token(uow, access_token)
    await UsersService().revoke_tokens(uow, user, user_id)
    return {"detail": "Tokens revoked"}
