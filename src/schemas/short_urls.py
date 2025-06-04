from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ShortURLCreate(BaseModel):
    original_url: HttpUrl
    expire_minutes: int | None = None
    clicks_left: int | None = None
    desired_short_code: str | None = None
    tag: str | None = None

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
    clicks_left: int | None = None
    is_active: bool
    tag: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )


class ShortURLFilters(BaseModel):
    short_code: str | None = None
    original_url: HttpUrl | None = None
    is_active: bool | None = None
    tag: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ShortURLDeactivateResponse(BaseModel):
    short_code: str

    model_config = ConfigDict(
        from_attributes=True,
    )
