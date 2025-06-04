from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from db.database import async_session_maker
from schemas.users import UserInfoResponseSchema
from services.auth import AuthService
from utils.unitofwork import IUnitOfWork, UnitOfWork


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


def get_uow():
    return UnitOfWork(async_session_maker)


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]


async def get_user_from_access_token(
    access_token: Annotated[str, Depends(oauth2_scheme)], uow: UOWDep
):
    user = await AuthService().get_user_by_access_token(uow, access_token)
    return user


UserFromAccessTokenDep = Annotated[
    UserInfoResponseSchema, Depends(get_user_from_access_token)
]

FormDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]
