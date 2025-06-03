from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    db_name: str = Field("postgres", env="DB_NAME")
    db_user: str = Field("postgres", env="DB_USER")
    db_password: str = Field("postgres", env="DB_PASSWORD")
    db_host: str = Field("localhost", env="DB_HOST")
    db_port: int = Field(5432, env="DB_PORT")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://"
            f"{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


class AuthJWT(BaseSettings):
    secret_key: str = Field("most secret key", env="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 5
    refresh_token_expire_minutes: int = 30


class UrlAliasSettings(BaseSettings):
    default_alias_expire_minutes: int = 1440


class Settings:
    db: DbSettings = DbSettings()
    auth_jwt: AuthJWT = AuthJWT()
    url_alias: UrlAliasSettings = UrlAliasSettings()

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
