from models.short_urls import ShortURLModel
from repositories.sql_alchemy_repository import SQLAlchemyRepository


class UrlsRepository(SQLAlchemyRepository):
    model = ShortURLModel
