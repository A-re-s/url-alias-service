from datetime import datetime, timedelta, timezone
from typing import List

from sqlalchemy import func, select

from models.click_stats import ClickStat
from models.short_urls import ShortURL
from schemas.short_urls import ShortURLFilters
from schemas.stat import URLClickStats
from schemas.users import UserInfoResponseSchema
from utils.unitofwork import IUnitOfWork


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

            urls_query = select(ShortURL).where(ShortURL.user_id == user.id)

            if filters.short_code:
                urls_query = urls_query.where(ShortURL.short_code == filters.short_code)
            if filters.original_url:
                urls_query = urls_query.where(
                    ShortURL.original_url == str(filters.original_url)
                )
            if filters.is_active is not None:
                urls_query = urls_query.where(ShortURL.is_active == filters.is_active)
            if filters.tag:
                urls_query = urls_query.where(ShortURL.tag == filters.tag)

            hour_clicks = (
                select(func.count())
                .select_from(ClickStat)
                .where(
                    ClickStat.short_url_id == ShortURL.id,
                    ClickStat.clicked_at >= hour_ago,
                )
                .scalar_subquery()
                .label("clicks_last_hour")
            )

            day_clicks = (
                select(func.count())
                .select_from(ClickStat)
                .where(
                    ClickStat.short_url_id == ShortURL.id,
                    ClickStat.clicked_at >= day_ago,
                )
                .scalar_subquery()
                .label("clicks_last_day")
            )

            query = (
                select(
                    ShortURL,
                    hour_clicks,
                    day_clicks,
                )
                .select_from(ShortURL)
                .order_by(day_clicks.desc())
            )

            offset = (filters.page - 1) * filters.page_size
            query = query.offset(offset).limit(filters.page_size)

            result = await uow.session.execute(query)
            rows = result.all()

            return [
                URLClickStats(
                    original_url=row.ShortURL.original_url,
                    short_code=row.ShortURL.short_code,
                    clicks_last_hour=row.clicks_last_hour or 0,
                    clicks_last_day=row.clicks_last_day or 0,
                )
                for row in rows
            ]
