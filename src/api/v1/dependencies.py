from typing import Annotated

from fastapi import Depends

from db.database import async_session_maker
from utils.unitofwork import IUnitOfWork, UnitOfWork


def get_uow():
    return UnitOfWork(async_session_maker)


UOWDep = Annotated[IUnitOfWork, Depends(get_uow)]
