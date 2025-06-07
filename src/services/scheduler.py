from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from db.database import db_manager
from models.short_urls import ShortURLModel


scheduler = AsyncIOScheduler()


async def delete_expired_links(session: AsyncSession):
    now = int(datetime.now().timestamp())
    await session.execute(
        ShortURLModel.__table__.delete().where(
            (ShortURLModel.expires_at <= now)
            | (ShortURLModel.clicks_left == 0)
            | (ShortURLModel.is_active is False)
        )
    )
    await session.commit()


@scheduler.scheduled_job(IntervalTrigger(days=1, start_date=datetime.now()))
async def scheduled_delete():
    async with db_manager.async_session_maker() as session:
        await delete_expired_links(session)
