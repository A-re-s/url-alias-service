from fastapi import APIRouter

from api.v1.users import token_router, users_router


all_routers = [users_router, token_router]
router_v1 = APIRouter(prefix="/v1", tags=["V1"])

for router in all_routers:
    router_v1.include_router(router)
