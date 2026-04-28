from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "ChiPulse"
    app_env: str = "development"
    database_url: str
    secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()