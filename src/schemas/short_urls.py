from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ShortURLCreate(BaseModel):
    original_url: HttpUrl
    expire_minutes: Optional[int] = Field(
        default=None, description="Link lifetime in minutes"
    )
    clicks_left: Optional[int] = Field(
        default=None, description="The maximum number of clicks on the link"
    )
    desired_short_code: Optional[str] = Field(
        default=None, description="Desired link short code"
    )
    tag: Optional[str] = Field(default=None, description="Tag for grouping links")

    @field_validator("desired_short_code")
    @classmethod
    def validate_no_tilde(cls, v: str) -> HttpUrl:
        if "~" in v:
            raise ValueError("Desired short code must not contain tilde (~) character")
        return v


class ShortURLInfo(BaseModel):
    short_code: str
    original_url: HttpUrl
    expires_at: int
    clicks_left: Optional[int] = Field(default=None)
    is_active: bool
    tag: Optional[str] = Field(default=None)

    model_config = ConfigDict(
        from_attributes=True,
    )


class ShortURLFilters(BaseModel):
    short_code: Optional[str] = Field(default=None)
    original_url: Optional[HttpUrl] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)
    tag: Optional[str] = Field(default=None, description="Tag for grouping links")
    page: Optional[int] = Field(default=1, ge=1)
    page_size: Optional[int] = Field(default=10, ge=1, le=100)


class ShortURLDeactivateResponse(BaseModel):
    short_code: str

    model_config = ConfigDict(
        from_attributes=True,
    )
