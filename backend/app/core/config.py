from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Food Store API"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./food_store.db"
    cors_origins: str = "http://localhost:5173"
    secret_key: str = "change-this-secret-key"
    access_token_expire_minutes: int = 60
    seed_admin_name: str = "Food Store Admin"
    seed_admin_email: str = "admin@foodstore.local"
    seed_admin_password: str = "Admin1234!"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
