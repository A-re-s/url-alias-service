from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class URLClickStats(BaseModel):
    """Schema for URL click statistics."""

    original_url: HttpUrl = Field(
        description="The original URL that was shortened",
        examples=["https://example.com/very/long/path?param=value"],
    )
    short_code: str = Field(
        description="The unique short code for the URL",
        examples=["abc123", "promo2024"],
    )
    clicks_last_hour: int = Field(
        description="Number of clicks in the last hour", examples=[42, 156, 789]
    )
    clicks_last_day: int = Field(
        description="Number of clicks in the last 24 hours", examples=[1234, 5678, 9012]
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "original_url": "https://example.com/very/long/path?param=value",
                    "short_code": "promo2024",
                    "clicks_last_hour": 42,
                    "clicks_last_day": 1234,
                },
                {
                    "original_url": "https://another-example.com/path",
                    "short_code": "abc123",
                    "clicks_last_hour": 156,
                    "clicks_last_day": 5678,
                },
            ]
        },
    )
