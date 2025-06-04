from pydantic import BaseModel, ConfigDict, HttpUrl


class ClickStatInfo(BaseModel):
    short_code: str
    original_url: HttpUrl
    clicks: int

    model_config = ConfigDict(
        from_attributes=True,
    )
