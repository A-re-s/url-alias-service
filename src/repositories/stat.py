from models.click_stats import ClickStatModel
from repositories.sql_alchemy_repository import SQLAlchemyRepository


class StatRepository(SQLAlchemyRepository):
    model = ClickStatModel
