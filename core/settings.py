from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    sqlalchemy_echo: bool
    jwt_key: str
    jwt_algo: str
    jwt_minutes: int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()  # type: ignore
