from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "orbit"

    # JWT
    JWT_SECRET: str = "change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # Hermes
    HERMES_API_URL: str = "http://localhost:8080"
    HERMES_API_KEY: str = ""

    # Application
    APP_DEBUG: bool = False
    CORS_ORIGINS: str = "http://localhost:5173"

    @property
    def database_url(self) -> str:
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
