from models.short_urls import ShortURL
from repositories.sql_alchemy_repository import SQLAlchemyRepository


class UrlsRepository(SQLAlchemyRepository):
    model = ShortURL
