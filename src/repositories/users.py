from models.users import UserModel
from repositories.sql_alchemy_repository import SQLAlchemyRepository


class UsersRepository(SQLAlchemyRepository):
    model = UserModel
