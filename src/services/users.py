from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError

from models.users import UserModel
from schemas.users import UserInfoResponseSchema, UserSchema
from utils.jwt_utils import jwt_service
from utils.unitofwork import IUnitOfWork


class UsersService:
    async def add_user(
        self, uow: IUnitOfWork, form_data: OAuth2PasswordRequestForm
    ) -> UserModel:
        username = form_data.username
        password = form_data.password
        hashed_password = jwt_service.hash_password(password)

        try:
            async with uow:
                user: UserSchema = await uow.users.add_one(
                    {"username": username, "password": hashed_password}
                )
                await uow.commit()
                return UserInfoResponseSchema(id=user.id, username=user.username)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this username already exists",
            )

    async def revoke_tokens(
        self, uow: IUnitOfWork, user: UserInfoResponseSchema, user_id: int
    ) -> UserModel:
        if user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This action can only be performed on your own account",
            )
        async with uow:
            await uow.users.edit_one(
                user_id, {"token_version": UserModel.token_version + 1}
            )
            await uow.commit()
