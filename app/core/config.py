from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def async_database_url(self) -> str:
        url = make_url(self.DATABASE_URL)
        return url.set(drivername="postgresql+asyncpg")


settings = Settings()
