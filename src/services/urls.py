from datetime import datetime, timedelta, timezone
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

from config import Settings
from models.short_urls import ShortURL
from schemas.short_urls import ShortURLCreate, ShortURLFilters, ShortURLInfo
from schemas.users import UserInfoResponseSchema
from utils.unitofwork import IUnitOfWork
from utils.url_utils import generate_short_code


class UrlService:
    async def add_url(
        self,
        uow: IUnitOfWork,
        url_info: ShortURLCreate,
        user: UserInfoResponseSchema,
        settings: Settings,
    ) -> ShortURLInfo:
        if url_info.expire_minutes is None:
            url_info.expire_minutes = settings.url_alias.default_alias_expire_minutes
        async with uow:
            payload = {
                "original_url": str(url_info.original_url),
                "user_id": user.id,
                "expires_at": int(
                    (
                        datetime.now(timezone.utc)
                        + timedelta(minutes=url_info.expire_minutes)
                    ).timestamp()
                ),
            }
            if url_info.tag is not None:
                payload["tag"] = url_info.tag
            if url_info.tag is not None:
                payload["clicks_left"] = url_info.clicks_left

            should_generate_short_code = True
            if url_info.desired_short_code is not None:
                used_short_code = await uow.urls.find_one(
                    short_code=url_info.desired_short_code
                )
                if used_short_code is None:
                    payload["short_code"] = url_info.desired_short_code
                    should_generate_short_code = False

            if should_generate_short_code:
                short_url: ShortURL = await uow.urls.add_one(payload)
                unique_short_code = generate_short_code(short_url.id)
                await uow.urls.edit_one(short_url.id, {"short_code": unique_short_code})
            else:
                try:
                    short_url: ShortURL = await uow.urls.add_one(payload)
                except IntegrityError:
                    payload.pop("short_code")
                    short_url: ShortURL = await uow.urls.add_one(payload)
                    unique_short_code = generate_short_code(short_url.id)
                    await uow.urls.edit_one(
                        short_url.id, {"short_code": unique_short_code}
                    )
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
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
                )

            if not url.is_active:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE, detail="URL is no longer active"
                )

            current_time = int(datetime.now(timezone.utc).timestamp())
            if url.expires_at and current_time > url.expires_at:
                raise HTTPException(
                    status_code=status.HTTP_410_GONE, detail="URL has expired"
                )

            if url.clicks_left is not None:
                if url.clicks_left <= 0:
                    raise HTTPException(
                        status_code=status.HTTP_410_GONE, detail="Click limit reached"
                    )
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
            filter_conditions = {"user_id": user.id}

            if filters.short_code:
                filter_conditions["short_code"] = filters.short_code
            if filters.original_url:
                filter_conditions["original_url"] = str(filters.original_url)
            if filters.is_active is not None:
                filter_conditions["is_active"] = filters.is_active
            if filters.tag:
                filter_conditions["tag"] = filters.tag
            offset = (filters.page - 1) * filters.page_size

            urls = await uow.urls.find_all(
                offset=offset, limit=filters.page_size, **filter_conditions
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
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="URL not found"
                )

            if url.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to deactivate this URL",
                )

            if not url.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="URL already deactivated",
                )

            await uow.urls.edit_one(url.id, {"is_active": False})
            await uow.commit()
