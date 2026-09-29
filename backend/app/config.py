from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./aquatrust.db"
    API_V1_PREFIX: str = "/api"
    PROJECT_NAME: str = "AquaTrust"

    class Config:
        env_file = ".env"


settings = Settings()
