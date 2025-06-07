from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import RedirectResponse

from api.v1.dependencies import UOWDep, UserFromAccessTokenDep
from config import SettingsDep
from schemas.short_urls import (
    ShortURLCreate,
    ShortURLFilters,
)
from services.urls import UrlService


urls_router = APIRouter(
    tags=["Urls"],
)
redirect_router = APIRouter()


@urls_router.post("/urls")
async def get_short_url(
    user: UserFromAccessTokenDep,
    url_info: ShortURLCreate,
    uow: UOWDep,
    settings: SettingsDep,
):
    res = await UrlService().add_url(uow, url_info, user, settings)
    return res


@urls_router.get("/urls")
async def get_created_urls(
    user: UserFromAccessTokenDep,
    uow: UOWDep,
    filters: Annotated[ShortURLFilters, Query()],
):
    """
    Get user's URLs with filtering and pagination.

    Query parameters:
    - short_code: Filter by short code
    - original_url: Filter by original URL
    - is_active: Filter by active status
    - tag: Filter by tag
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)
    """
    return await UrlService().get_user_urls(uow, user, filters)


@redirect_router.get("/{short_code}")
async def redirect_to_url(
    short_code: str,
    uow: UOWDep,
) -> RedirectResponse:
    """
    Redirect to original URL if the short code is valid and active.
    Handles click tracking and validation.
    """
    original_url = await UrlService().get_redirect_url(uow, short_code)
    return RedirectResponse(url=original_url)


@urls_router.patch("/urls/{short_code}")
async def deactivate_url(
    short_code: str,
    user: UserFromAccessTokenDep,
    uow: UOWDep,
):
    """
    Deactivate a short URL.
    Only the owner of the URL can deactivate it.
    """
    await UrlService().deactivate_url(uow, user, short_code)
    return {"message": "Short URL deactivated successfully"}
