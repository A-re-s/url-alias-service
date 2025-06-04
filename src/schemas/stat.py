from pydantic import BaseModel, ConfigDict, HttpUrl


class URLClickStats(BaseModel):
    original_url: HttpUrl
    short_code: str
    clicks_last_hour: int
    clicks_last_day: int

    model_config = ConfigDict(
        from_attributes=True,
    )
