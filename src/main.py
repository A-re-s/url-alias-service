from fastapi import FastAPI

from api.main_router import main_router
from core.exceptions import register_exception_handlers
from core.lifespan import db_init


app = FastAPI(
    lifespan=db_init,
    title="URL Alias Service",
    version="1.0",
)

app.include_router(main_router)
register_exception_handlers(app)
