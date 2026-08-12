from dotenv import find_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=find_dotenv(),
    )

    # DB_HOST: str
    # DB_PORT: str
    # DB_USER: str
    # DB_PASS: str
    # DB_NAME: str
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # @property
    # def ASYNC_DATABASE_URL(self):
    #     return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    @property
    def async_database_url(self) -> str:
        url = make_url(self.DATABASE_URL)
        return url.set(drivername="postgresql+asyncpg")

    # @property
    # def sync_database_url(self) -> str:
    #     url = make_url(self.DATABASE_URL)
    #     return str(url.set(drivername="postgresql+psycopg2"))

settings = Settings()
