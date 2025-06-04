from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from schemas.users import (
    TokenObtainPairSchema,
    TokenType,
    UserInfoResponseSchema,
)
from utils.jwt_utils import jwt_service
from utils.unitofwork import IUnitOfWork


class AuthService:
    async def obtain_tokens_by_credentials(
        self, uow: IUnitOfWork, form_data: OAuth2PasswordRequestForm
    ) -> TokenObtainPairSchema:
        dummy_hash = "$2b$12$DummyHashDummyHashDummyHac"
        async with uow:
            user = await uow.users.find_one(username=form_data.username)

            if not user or not jwt_service.validate_password(
                form_data.password, user.password if user else dummy_hash
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            return jwt_service.create_token_pair(user.id, user.token_version)

    async def get_user_by_access_token(
        self, uow: IUnitOfWork, token: str
    ) -> UserInfoResponseSchema:
        token_payload = jwt_service.decode_jwt(token)
        jwt_service.validate_token_type(token_payload, TokenType.ACCESS)
        async with uow:
            user = await uow.users.find_one(id=token_payload.id)
            jwt_service.validate_token_version(token_payload, user.token_version)
            response = UserInfoResponseSchema(id=user.id, username=user.username)
            return response

    async def refresh_tokens(
        self, uow: IUnitOfWork, refresh_token: str
    ) -> TokenObtainPairSchema:
        token_payload = jwt_service.decode_jwt(refresh_token)
        jwt_service.validate_token_type(token_payload, TokenType.REFRESH)
        async with uow:
            user = await uow.users.find_one(id=token_payload.id)
            jwt_service.validate_token_version(token_payload, user.token_version)
            return jwt_service.create_token_pair(user.id, user.token_version)
