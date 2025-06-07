from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from db.database import db_manager
from services.scheduler import scheduler


@asynccontextmanager
async def db_init(app: FastAPI) -> AsyncGenerator[None, None]:
    await db_manager.connect()
    scheduler.start()
    yield
    scheduler.shutdown()
    await db_manager.close()
