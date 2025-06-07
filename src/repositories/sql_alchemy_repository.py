from typing import List

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from repositories.abstract_repository import AbstractRepository


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_one(self, data: dict) -> int:
        stmt = insert(self.model).values(**data).returning(self.model)
        res = await self.session.execute(stmt)
        return res.scalar_one()

    async def edit_one(self, elem_id: int, data: dict) -> int:
        stmt = update(self.model).values(**data).filter_by(id=elem_id)
        await self.session.execute(stmt)

    async def find_all(
        self, offset: int = 0, limit: int | None = None, **filter_by
    ) -> List:
        stmt = select(self.model).filter_by(**filter_by)

        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_one(self, **filter_by):
        stmt = select(self.model).filter_by(**filter_by)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
