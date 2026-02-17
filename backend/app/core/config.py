from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DSN: str = "postgresql://f1user:strongpassword@localhost:5432/f1db"


settings = Settings()
