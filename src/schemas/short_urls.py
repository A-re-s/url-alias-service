from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class ShortURLCreate(BaseModel):
    """Schema for creating a new short URL."""

    original_url: HttpUrl = Field(
        description="The original URL to be shortened",
        examples=["https://example.com/very/long/path?param=value"],
    )
    expire_minutes: Optional[int] = Field(
        default=None,
        description="Link lifetime in minutes. If not set, the link will have default expiration time.",
        examples=[60, 1440, 10080],  # 1 hour, 1 day, 1 week
    )
    clicks_left: Optional[int] = Field(
        default=None,
        description="The maximum number of clicks allowed for this link. If not set, unlimited clicks are allowed.",
        examples=[100, 1000, 10000],
    )
    desired_short_code: Optional[str] = Field(
        default=None,
        description="Custom short code for the URL. If not provided, a random code will be generated.",
        examples=["my-link", "promo2024", "product-123"],
    )
    tag: Optional[str] = Field(
        default=None,
        description="Optional tag for grouping and filtering links",
        examples=["marketing", "social", "documentation"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "original_url": "https://example.com/very/long/path?param=value",
                    "expire_minutes": 1440,
                    "clicks_left": 1000,
                    "desired_short_code": "promo2024",
                    "tag": "marketing",
                }
            ]
        }
    )

    @field_validator("desired_short_code")
    @classmethod
    def validate_no_tilde(cls, v: str) -> HttpUrl:
        if "~" in v:
            raise ValueError("Desired short code must not contain tilde (~) character")
        return v


class ShortURLInfo(BaseModel):
    """Schema for short URL information response."""

    short_code: str = Field(
        description="Unique shortened URL code",
        examples=["abc123", "promo2024", "my-link"],
    )
    original_url: HttpUrl = Field(
        description="The original URL that was shortened",
        examples=["https://example.com/very/long/path?param=value"],
    )
    expires_at: int = Field(
        description="Unix timestamp when the URL will expire.", examples=[1712345678]
    )
    clicks_left: Optional[int] = Field(
        default=None,
        description="Number of clicks remaining before the link becomes inactive. None means unlimited.",
        examples=[42, 999, None],
    )
    is_active: bool = Field(
        description="Whether the short URL is currently active and can be used",
        examples=[True, False],
    )
    tag: Optional[str] = Field(
        default=None,
        description="Optional tag used for grouping links",
        examples=["marketing", "social", "documentation"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "short_code": "promo2024",
                    "original_url": "https://example.com/very/long/path?param=value",
                    "expires_at": 1712345678,
                    "clicks_left": 42,
                    "is_active": True,
                    "tag": "marketing",
                }
            ]
        },
    )


class ShortURLFilters(BaseModel):
    """Schema for filtering short URLs in list operations."""

    short_code: Optional[str] = Field(
        default=None,
        description="Filter by exact short code",
        examples=["abc123", "promo2024"],
    )
    original_url: Optional[HttpUrl] = Field(
        default=None,
        description="Filter by original URL",
        examples=["https://example.com"],
    )
    is_active: Optional[bool] = Field(
        default=None, description="Filter by URL active status", examples=[True, False]
    )
    tag: Optional[str] = Field(
        default=None, description="Filter URLs by tag", examples=["marketing", "social"]
    )
    page: Optional[int] = Field(
        default=1, ge=1, description="Page number for pagination", examples=[1, 2, 3]
    )
    page_size: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of items per page (1-100)",
        examples=[10, 20, 50],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {"tag": "marketing", "is_active": True, "page": 1, "page_size": 20}
            ]
        }
    )


class ShortURLDeactivateResponse(BaseModel):
    """Schema for deactivate URL response."""

    short_code: str = Field(
        description="Short code for the deactivation", examples=["abc123", "promo2024"]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"examples": [{"short_code": "promo2024"}]},
    )
