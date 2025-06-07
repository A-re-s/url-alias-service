from typing import Annotated

from fastapi import APIRouter, Query, status
from fastapi.responses import RedirectResponse

from api.v1.dependencies import UOWDep, UserFromAccessTokenDep
from config import SettingsDep
from schemas.short_urls import (
    ShortURLCreate,
    ShortURLFilters,
    ShortURLInfo,
)
from services.urls import UrlService


urls_router = APIRouter(
    tags=["Urls"],
)
redirect_router = APIRouter()


@urls_router.post(
    "/urls",
    response_model=ShortURLInfo,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Short URL created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "short_code": "promo2024",
                        "original_url": "https://example.com/very/long/path?param=value",
                        "expires_at": 1712345678,
                        "clicks_left": 1000,
                        "is_active": True,
                        "tag": "marketing",
                    }
                }
            },
        },
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {"detail": "Desired short code is already in use."}
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def get_short_url(
    user: UserFromAccessTokenDep,
    url_info: ShortURLCreate,
    uow: UOWDep,
    settings: SettingsDep,
):
    """
    Create a new short URL.

    Parameters:
    - url_info: Information about the URL to shorten
        - original_url: The URL to shorten
        - expire_minutes: Optional expiration time in minutes
        - clicks_left: Optional maximum number of clicks
        - desired_short_code: Optional custom short code
        - tag: Optional tag for grouping

    Returns:
    - ShortURLInfo object containing the generated short URL details
    """
    res = await UrlService().add_url(uow, url_info, user, settings)
    return res


@urls_router.get(
    "/urls",
    response_model=list[ShortURLInfo],
    responses={
        200: {
            "description": "List of user's URLs",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "short_code": "promo2024",
                            "original_url": "https://example.com/path1",
                            "expires_at": 1712345678,
                            "clicks_left": 42,
                            "is_active": True,
                            "tag": "marketing",
                        },
                        {
                            "short_code": "docs123",
                            "original_url": "https://example.com/path2",
                            "expires_at": 1712345679,
                            "clicks_left": None,
                            "is_active": True,
                            "tag": "documentation",
                        },
                    ]
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {
                "application/json": {"example": {"detail": "Not authenticated"}}
            },
        },
    },
)
async def get_created_urls(
    user: UserFromAccessTokenDep,
    uow: UOWDep,
    filters: Annotated[ShortURLFilters, Query()],
):
    """
    Get user's URLs with filtering and pagination.

    Query parameters:
    - short_code: Filter by exact short code
    - original_url: Filter by original URL
    - is_active: Filter by URL active status
    - tag: Filter by tag
    - page: Page number (default: 1)
    - page_size: Items per page (default: 10, max: 100)

    Returns:
    - List of ShortURLInfo objects containing URL details
    """
    return await UrlService().get_user_urls(uow, user, filters)


@redirect_router.get(
    "/{short_code}",
    response_class=RedirectResponse,
    responses={
        307: {"description": "Temporary redirect to the original URL"},
        404: {
            "description": "Short code not found",
            "content": {"application/json": {"example": {"detail": "URL not found"}}},
        },
        410: {
            "description": "URL expired or inactive",
            "content": {
                "application/json": {
                    "examples": {
                        "expired": {"value": {"detail": "URL has expired"}},
                        "inactive": {"value": {"detail": "URL is no longer active"}},
                        "clicks": {"value": {"detail": "Click limit reached"}},
                    }
                }
            },
        },
    },
)
async def redirect_to_url(
    short_code: str,
    uow: UOWDep,
) -> RedirectResponse:
    """
    Redirect to the original URL associated with the short code.

    Parameters:
    - short_code: The unique identifier for the shortened URL

    Returns:
    - HTTP 307 redirect to the original URL if valid
    - HTTP 404 if the short code is not found
    - HTTP 410 if the URL has expired or reached click limit
    """
    original_url = await UrlService().get_redirect_url(uow, short_code)
    return RedirectResponse(url=original_url)


@urls_router.patch(
    "/urls/{short_code}",
    responses={
        200: {
            "description": "URL deactivated successfully",
            "content": {
                "application/json": {
                    "example": {"message": "Short URL deactivated successfully"}
                }
            },
        },
        403: {
            "description": "Forbidden",
            "content": {
                "application/json": {
                    "examples": {
                        "permission": {
                            "value": {
                                "detail": "You don't have permission to deactivate this URL"
                            }
                        },
                        "already_deactivated": {
                            "value": {"detail": "URL already deactivated"}
                        },
                    }
                }
            },
        },
        404: {
            "description": "URL not found",
            "content": {"application/json": {"example": {"detail": "URL not found"}}},
        },
    },
)
async def deactivate_url(
    short_code: str,
    user: UserFromAccessTokenDep,
    uow: UOWDep,
):
    """
    Deactivate a short URL.

    Parameters:
    - short_code: The unique identifier of the URL to deactivate
    - user: Current authenticated user (must be the URL owner)

    Returns:
    - Success message if deactivation is successful
    - HTTP 404 if URL not found
    - HTTP 403 if user is not the URL owner or URL is already deactivated
    """
    await UrlService().deactivate_url(uow, user, short_code)
    return {"message": "Short URL deactivated successfully"}
