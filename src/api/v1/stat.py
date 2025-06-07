from typing import Annotated, List

from fastapi import APIRouter, Query

from api.v1.dependencies import UOWDep, UserFromAccessTokenDep
from schemas.short_urls import (
    ShortURLFilters,
)
from schemas.stat import URLClickStats
from services.stat import StatService


stat_router = APIRouter(
    tags=["Stat"],
)


@stat_router.get("/urls/stats", response_model=List[URLClickStats])
async def get_url_statistics(
    user: UserFromAccessTokenDep,
    uow: UOWDep,
    filters: Annotated[ShortURLFilters, Query()],
):
    """
    Get click statistics for user's URLs.
    Returns URLs sorted by click count (most clicked first).

    Query parameters:
    - short_code: Filter by short code
    - original_url: Filter by original URL
    - is_active: Filter by active status
    - tag: Filter by tag
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)

    Returns:
    - List of URLs with click statistics:
        - original_url: Original URL
        - short_code: Short code
        - clicks_last_hour: Number of clicks in the last hour
        - clicks_last_day: Number of clicks in the last 24 hours
    """
    return await StatService().get_click_statistics(uow, user, filters)
