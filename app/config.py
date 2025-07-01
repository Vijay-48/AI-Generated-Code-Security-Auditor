import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_REFERER: str = os.getenv("OPENROUTER_REFERER", "http://localhost:8000")
    OPENROUTER_TITLE: str = os.getenv("OPENROUTER_TITLE", "AI Code Security Auditor")
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    BANDIT_CONFIG_PATH: str = "./configs/bandit.yaml"
    SEMGREP_RULES_PATH: str = "./configs/semgrep-rules"

    class Config:
        env_file = ".env"

settings = Settings()