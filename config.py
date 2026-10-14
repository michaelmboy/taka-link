from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
class Settings(BaseSettings):
    database_url: str = "sqlite:///./takalink.db"
    secret_key: str = "local-only-change-this-secret"
    frontend_origin: str = "http://localhost:3000"
    cookie_secure: bool = False
    cookie_samesite: str = "lax"
    token_expire_minutes: int = 60 * 24 * 7
    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
settings = Settings()
