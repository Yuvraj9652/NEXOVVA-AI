from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "NEXOVVA AI Service"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8001
    GEMINI_API_KEY: str
    MODEL_NAME: str = "gemini-2.5-flash"
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
