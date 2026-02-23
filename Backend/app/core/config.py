from typing import List

# pydantic v2 moved BaseSettings into the pydantic-settings package.
# Try to import from pydantic_settings first, fall back to pydantic for older installs.
try:
    from pydantic_settings import BaseSettings
    from pydantic import AnyHttpUrl
except Exception:
    from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings): # pyright: ignore[reportGeneralTypeIssues, reportUntypedBaseClass]
    MONGO_URI: str
    DATABASE_NAME: str = "ai_chat"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    OPENROUTER_API_KEY: str
    OPENROUTER_URL: AnyHttpUrl = "https://api.openrouter.ai/v1/chat/completions" # pyright: ignore[reportAssignmentType]
    # Development helper: when true, the app will not call the external LLM
    # provider and will use a local mock stream instead. Useful when offline or
    # to avoid DNS/connect errors during development.
    USE_MOCK_LLM: bool = False
    CORS_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
