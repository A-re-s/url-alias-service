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


@stat_router.get(
    "/urls/stats",
    response_model=List[URLClickStats],
    responses={
        200: {
            "description": "URL click statistics retrieved successfully",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "original_url": "https://example.com/path1",
                            "short_code": "promo2024",
                            "clicks_last_hour": 42,
                            "clicks_last_day": 1234,
                        },
                        {
                            "original_url": "https://example.com/path2",
                            "short_code": "docs123",
                            "clicks_last_hour": 156,
                            "clicks_last_day": 5678,
                        },
                    ]
                }
            },
        },
        401: {
            "description": "Not authenticated",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def get_url_statistics(
    user: UserFromAccessTokenDep,
    uow: UOWDep,
    filters: Annotated[ShortURLFilters, Query()],
):
    """
    Get click statistics for user's URLs with filtering and pagination.
    URLs are sorted by click count in descending order (most clicked first).

    Parameters:
    - user: Current authenticated user
    - filters: Query parameters for filtering URLs
        - short_code: Filter by exact short code
        - original_url: Filter by original URL
        - is_active: Filter by URL active status
        - tag: Filter by tag
        - page: Page number (default: 1)
        - page_size: Items per page (default: 10, max: 100)

    Returns:
    - List of URLClickStats objects containing:
        - original_url: The original URL that was shortened
        - short_code: The unique short code for the URL
        - clicks_last_hour: Number of clicks in the last hour
        - clicks_last_day: Number of clicks in the last 24 hours

    Notes:
    - Only URLs owned by the authenticated user are included
    - Click counts are updated in real-time
    - Inactive or expired URLs are included unless filtered out
    """
    return await StatService().get_click_statistics(uow, user, filters)
