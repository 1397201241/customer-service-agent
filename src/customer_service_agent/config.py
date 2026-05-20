"""Configuration settings for the customer service agent."""

import os

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM Provider: openai | minimax
    llm_provider: str = "openai"

    # OpenAI settings
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"

    # MiniMax settings
    minimax_api_key: str | None = None
    minimax_base_url: str = "https://api.minimax.chat/v1"
    minimax_model: str = "MiniMax-Text-01"

    # Common LLM settings
    temperature: float = 0.3

    # Data directory
    data_dir: str = "./data"

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
