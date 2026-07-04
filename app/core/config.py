from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "PulseAI"
    DEBUG: bool = True
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama3-8b-8192"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
