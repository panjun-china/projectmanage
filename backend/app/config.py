from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "项目管理平台"
    API_PREFIX: str = "/api"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    DATABASE_URL: str = "sqlite:///./projectmanage.db"

    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024

    class Config:
        env_file = ".env"


settings = Settings()
