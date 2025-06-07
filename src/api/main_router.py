from fastapi import APIRouter

from api.v1.routers import router_v1
from api.v1.short_urls import redirect_router


main_router = APIRouter()

main_router.include_router(router_v1, prefix="/api")


@main_router.get("/ping", tags=["Ping"])
def health_check():
    return {"message": "pong"}


main_router.include_router(redirect_router)
