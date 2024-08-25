from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # default setting values in case there are no .env files
    environment: str = "dev",
    base_url: str = "http://127.0.0.1:8080"
    db_url: str = "sqlite:///./shortener.db"
    jwt_secret_key: str = None
    jwt_token_expiry_in_minutes: int = 60
    fastapi_port: int = 8080

    # load the class with the .env file values
    # since we are using pydantic, the values will also be type
    # checked against the schema specified in this Settings class
    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    setting = Settings()

    print(f"{setting.environment} settings loaded...")
    return setting
