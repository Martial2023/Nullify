from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # API
    app_name: str = "Nullify API"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]

    # OpenRouter
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "anthropic/claude-sonnet-4-5"

    # Database
    database_url: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
