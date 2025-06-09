from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgresql_url: str
    smtp_user: str
    smtp_password: str
    email_from: str
    redis_host: str
    redis_port: int
    session_expire_seconds: int
    redis_password: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
