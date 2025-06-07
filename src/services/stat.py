from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import case, func, select

from models.click_stats import ClickStatModel
from models.short_urls import ShortURLModel
from schemas.short_urls import ShortURLFilters
from schemas.stat import URLClickStats
from schemas.users import UserInfoResponseSchema
from utils.unitofwork import IUnitOfWork
from utils.url_utils import build_short_url_filters


class StatService:

    async def get_click_statistics(
        self, uow: IUnitOfWork, user: UserInfoResponseSchema, filters: ShortURLFilters
    ) -> List[URLClickStats]:
        """
        Get click statistics for user's URLs.
        Returns URLs sorted by click count (most clicked first).
        """
        async with uow:
            hour_ago = int(
                (datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()
            )
            day_ago = int((datetime.now(timezone.utc) - timedelta(days=1)).timestamp())

            conditions = build_short_url_filters(user.id, filters)

            hour_case = case((ClickStatModel.clicked_at >= hour_ago, 1), else_=0)
            day_case = case((ClickStatModel.clicked_at >= day_ago, 1), else_=0)

            query = (
                select(
                    ShortURLModel.id,
                    ShortURLModel.original_url,
                    ShortURLModel.short_code,
                    func.sum(hour_case).label("clicks_last_hour"),
                    func.sum(day_case).label("clicks_last_day"),
                )
                .outerjoin(
                    ClickStatModel, ShortURLModel.id == ClickStatModel.short_url_id
                )
                .where(conditions)
                .group_by(ShortURLModel.id)
                .order_by(func.sum(day_case).desc())
            )

            offset = (filters.page - 1) * filters.page_size
            query = query.offset(offset).limit(filters.page_size)

            result = await uow.session.execute(query)
            rows = result.all()

            return [
                URLClickStats(
                    original_url=row.original_url,
                    short_code=row.short_code,
                    clicks_last_hour=row.clicks_last_hour or 0,
                    clicks_last_day=row.clicks_last_day or 0,
                )
                for row in rows
            ]
