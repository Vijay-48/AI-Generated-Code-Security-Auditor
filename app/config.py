import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite:///./security_auditor.db"

    # OpenRouter Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    OPENROUTER_REFERER: str = os.getenv("OPENROUTER_REFERER", "http://localhost:8000")
    OPENROUTER_TITLE: str = os.getenv("OPENROUTER_TITLE", "AI Code Security Auditor")
    OPENROUTER_MODELS: str = os.getenv("OPENROUTER_MODELS", "agentica-org/deepcoder-14b-preview:free,moonshotai/kimi-dev-72b:free,qwen/qwen-2.5-coder-32b-instruct:free,meta-llama/llama-3.3-70b-instruct:free")
    
    # GitHub Configuration
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    GITHUB_WEBHOOK_SECRET: str = os.getenv("GITHUB_WEBHOOK_SECRET", "")

    # ChromaDB Configuration
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"

    # Security Scanner Configuration
    BANDIT_CONFIG_PATH: str = "./configs/bandit.yaml"
    SEMGREP_RULES_PATH: str = "./configs/semgrep-rules"

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    
    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/1")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/2")
    
    # Cache Configuration
    CACHE_TTL_SCAN_RESULTS: int = int(os.getenv("CACHE_TTL_SCAN_RESULTS", "3600"))  # 1 hour
    CACHE_TTL_LLM_RESPONSES: int = int(os.getenv("CACHE_TTL_LLM_RESPONSES", "86400"))  # 24 hours
    CACHE_TTL_PATCHES: int = int(os.getenv("CACHE_TTL_PATCHES", "604800"))  # 7 days
    
    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_TIMEOUT: int = 60

    class Config:
        env_file = ".env"

settings = Settings()