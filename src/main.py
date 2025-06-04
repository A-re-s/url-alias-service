import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from api.v1.routers import router_v1
from api.v1.short_urls import redirect_router
from db.database import Base, engine


load_dotenv()


@asynccontextmanager
async def test_db_connection(*args):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield
    except Exception as e:
        print("❌DB connection failed")
        print(e)
    finally:
        await engine.dispose()


app = FastAPI(
    lifespan=test_db_connection,
    title="URL Alias Service",
    version="1.0",
)

app.include_router(router_v1, prefix="/api")
app.include_router(redirect_router)


@app.get("/ping", tags=["Ping"])
def health_check():
    return {"message": "pong"}


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."},
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("API_PORT", "8000")))
