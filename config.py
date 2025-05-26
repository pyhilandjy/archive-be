from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgresql_url: str
    secret_key: str
    jwt_algorithm: str
    access_token_expire_seconds: int
    smtp_user: str
    smtp_password: str
    email_from: str
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
