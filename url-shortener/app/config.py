from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    public_base_url: str = "http://localhost:8000"
    short_code_length: int = 7
    max_long_url_length: int = 2048


settings = Settings()
