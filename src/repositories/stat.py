from models.click_stats import ClickStat
from repositories.sql_alchemy_repository import SQLAlchemyRepository


class StatRepository(SQLAlchemyRepository):
    model = ClickStat
