from pydantic import BaseModel, ConfigDict, HttpUrl


class URLClickStats(BaseModel):
    original_url: HttpUrl
    short_code: str
    clicks_last_hour: int
    clicks_last_day: int

    model_config = ConfigDict(
        from_attributes=True,
    )


class ClickStatInfo(BaseModel):
    short_code: str
    original_url: HttpUrl
    clicks: int

    model_config = ConfigDict(from_attributes=True, extra="forbid")
