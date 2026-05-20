"""Configuration settings for the customer service agent."""

import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load Hermes env first (contains MiniMax keys), then local .env
load_dotenv(os.path.expanduser("~/.hermes/.env"))
load_dotenv()


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider: openai | minimax-cn
    llm_provider: str = "openai"

    # OpenAI settings
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # MiniMax China settings (Anthropic-compatible endpoint)
    minimax_cn_api_key: str | None = None
    minimax_cn_base_url: str = "https://api.minimaxi.com/anthropic"
    minimax_cn_model: str = "MiniMax-M2.7"

    # Common LLM settings
    temperature: float = 0.3

    # Data directory
    data_dir: str = "./data"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra env vars from ~/.hermes/.env


settings = Settings()
