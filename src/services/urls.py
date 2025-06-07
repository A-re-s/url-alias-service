from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status

from config import Settings
from models.short_urls import ShortURLModel
from schemas.short_urls import ShortURLCreate, ShortURLFilters, ShortURLInfo
from schemas.users import UserInfoResponseSchema
from utils.unitofwork import IUnitOfWork
from utils.url_utils import build_short_url_filters, generate_short_code


URL_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
)
URL_NOT_ACTIVE = HTTPException(
    status_code=status.HTTP_410_GONE, detail="URL is no longer active"
)
URL_EXPIRED = HTTPException(status_code=status.HTTP_410_GONE, detail="URL has expired")
CLICKS_LIMIT_REACHED = HTTPException(
    status_code=status.HTTP_410_GONE, detail="Click limit reached"
)
URL_ALREADY_DEACTIVATED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="URL already deactivated",
)
PERMISSION_DENIED = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="You don't have permission to deactivate this URL",
)
SHORT_CODE_ALREADY_USED = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Desired short code is already in use.",
)


class UrlService:
    async def add_url(
        self,
        uow: IUnitOfWork,
        url_info: ShortURLCreate,
        user: UserInfoResponseSchema,
        settings: Settings,
    ) -> ShortURLInfo:
        expire_minutes = (
            url_info.expire_minutes or settings.url_alias.default_alias_expire_minutes
        )
        expires_at = int(
            (datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)).timestamp()
        )

        payload = {
            "original_url": str(url_info.original_url),
            "user_id": user.id,
            "expires_at": expires_at,
            "tag": url_info.tag,
            "clicks_left": url_info.clicks_left,
        }
        async with uow:
            short_code = url_info.desired_short_code
            if short_code:
                existing_url = await uow.urls.find_one(short_code=short_code)
                if existing_url:
                    raise SHORT_CODE_ALREADY_USED
                payload["short_code"] = short_code

            short_url: ShortURLModel = await uow.urls.add_one(payload)
            if not short_code:
                generated_code = generate_short_code(short_url.id)
                await uow.urls.edit_one(short_url.id, {"short_code": generated_code})
            await uow.commit()
            return ShortURLInfo.model_validate(short_url)

    async def get_redirect_url(
        self,
        uow: IUnitOfWork,
        short_code: str,
    ) -> str:
        """Get original URL and handle click tracking for redirection."""
        async with uow:
            url = await uow.urls.find_one(short_code=short_code)
            if not url:
                raise URL_NOT_FOUND

            if not url.is_active:
                raise URL_NOT_ACTIVE

            current_time = int(datetime.now(timezone.utc).timestamp())
            if url.expires_at and current_time > url.expires_at:
                raise URL_EXPIRED

            if url.clicks_left is not None:
                if url.clicks_left <= 0:
                    raise CLICKS_LIMIT_REACHED
                await uow.urls.edit_one(url.id, {"clicks_left": url.clicks_left - 1})

            click_time = int(datetime.now(timezone.utc).timestamp())
            await uow.stat.add_one({"short_url_id": url.id, "clicked_at": click_time})

            await uow.commit()
            return str(url.original_url)

    async def get_user_urls(
        self, uow: IUnitOfWork, user: UserInfoResponseSchema, filters: ShortURLFilters
    ) -> List[ShortURLInfo]:
        """Get user's URLs with filtering and pagination."""
        async with uow:
            conditions = build_short_url_filters(user.id, filters)
            urls = await uow.urls.find_all(
                filter_expr=conditions,
                offset=(filters.page - 1) * filters.page_size,
                limit=filters.page_size,
            )

            return [ShortURLInfo.model_validate(url) for url in urls]

    async def deactivate_url(
        self,
        uow: IUnitOfWork,
        user: UserInfoResponseSchema,
        short_code: str,
    ):
        """Deactivate a short URL if it belongs to the user."""
        async with uow:
            url = await uow.urls.find_one(short_code=short_code)
            if not url:
                raise URL_NOT_FOUND

            if url.user_id != user.id:
                raise PERMISSION_DENIED

            if not url.is_active:
                raise URL_ALREADY_DEACTIVATED

            await uow.urls.edit_one(url.id, {"is_active": False})
            await uow.commit()
