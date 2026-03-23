import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_TITLE: str = "AI Code Security Auditor"
    API_VERSION: str = "2.0.0"
    
    # OpenRouter API Configuration
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
    OPENROUTER_REFERER: str = os.getenv("OPENROUTER_REFERER", "http://localhost:8000")
    OPENROUTER_TITLE: str = os.getenv("OPENROUTER_TITLE", "AI Code Security Auditor")
    
    # GroqCloud API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1/chat/completions")
    
    # OpenAI API Configuration (optional)
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Model Configuration - Primary Models
    MODEL_PATCH_GENERATION: str = os.getenv("MODEL_PATCH_GENERATION", "groq/compound")
    MODEL_QUALITY_ASSESSMENT: str = os.getenv("MODEL_QUALITY_ASSESSMENT", "qwen/qwen-2.5-72b-instruct")
    MODEL_FAST_CLASSIFICATION: str = os.getenv("MODEL_FAST_CLASSIFICATION", "llama-3.1-8b-instant")
    MODEL_CODE_GENERATION: str = os.getenv("MODEL_CODE_GENERATION", "qwen/qwen-2.5-coder-32b-instruct")
    MODEL_SECURITY_ANALYSIS: str = os.getenv("MODEL_SECURITY_ANALYSIS", "openai/gpt-oss-20b")
    MODEL_DETAILED_EXPLANATION: str = os.getenv("MODEL_DETAILED_EXPLANATION", "meta-llama/llama-3.3-70b-instruct")
    
    # Model Configuration - Secondary/Fallback Models
    MODEL_PATCH_GENERATION_SECONDARY: str = os.getenv("MODEL_PATCH_GENERATION_SECONDARY", "qwen/qwen-2.5-coder-32b-instruct")
    MODEL_QUALITY_ASSESSMENT_SECONDARY: str = os.getenv("MODEL_QUALITY_ASSESSMENT_SECONDARY", "meta-llama/llama-3.3-70b-instruct")
    MODEL_FAST_CLASSIFICATION_SECONDARY: str = os.getenv("MODEL_FAST_CLASSIFICATION_SECONDARY", "qwen/qwen-2.5-coder-32b-instruct")
    MODEL_DETAILED_EXPLANATION_SECONDARY: str = os.getenv("MODEL_DETAILED_EXPLANATION_SECONDARY", "qwen/qwen-2.5-72b-instruct")
    
    # Available Models Configuration
    DEFAULT_MODEL: str = os.getenv("MODEL_CODE_GENERATION", "qwen/qwen-2.5-coder-32b-instruct")
    AVAILABLE_MODELS: dict = {
        # GroqCloud Models
        "groq/compound": "Groq Compound - Built-in Python code execution for patches",
        "groq/compound-mini": "Groq Compound Mini - Lightweight code execution",
        "openai/gpt-oss-20b": "GPT-OSS 20B - Strong multi-purpose with code execution",
        "openai/gpt-oss-120b": "GPT-OSS 120B - Large model with Python execution",
        "llama-3.1-8b-instant": "LLaMA 3.1 8B - Ultra-fast classification",
        "llama-3.3-70b-versatile": "LLaMA 3.3 70B - Advanced reasoning",
        "meta-llama/llama-4-scout-17b": "LLaMA 4 Scout 17B - Advanced analysis",
        "qwen/qwen3-32b": "Qwen3 32B - General reasoning, multilingual",
        "moonshotai/kimi-k2-instruct": "Kimi K2 - Versatile chat and reasoning",
        
        # OpenRouter Models
        "qwen/qwen-2.5-coder-32b-instruct": "Qwen2.5 Coder 32B - Optimized for code generation",
        "qwen/qwen-3-coder-480b-a35b": "Qwen3 Coder 480B - Cutting edge for code",
        "qwen/qwen-2.5-72b-instruct": "Qwen2.5 72B - High coding & math capabilities",
        "meta-llama/llama-3.3-70b-instruct": "LLaMA 3.3 70B - Multilingual, instruction-tuned",
        "mistralai/mistral-nemo": "Mistral Nemo 12B - 128K context, multilingual",
        "meta-llama/llama-3.2-3b-instruct": "LLaMA 3.2 3B - Efficient NLP/coding",
        "deepseek/deepseek-v3.1": "DeepSeek V3.1 - Advanced free AI model",
        "moonshotai/kimi-dev-72b": "Kimi Dev 72B - Code and chat applications",
        "nvidia/nemotron-nano-9b-v2": "NVIDIA Nemotron Nano 9B - High utility for coding",
        "z-ai/glm-4.5-air": "GLM 4.5 Air - Free, code and research"
    }
    
    # Security Scanner Configuration
    SUPPORTED_LANGUAGES: list = ["python", "javascript", "java", "go", "typescript"]
    MAX_FILE_SIZE_MB: int = 10
    SCAN_TIMEOUT_SECONDS: int = 300

    # Redis/Cache Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    CACHE_TTL_SCAN_RESULTS: int = int(os.getenv("CACHE_TTL_SCAN_RESULTS", "3600"))
    CACHE_TTL_LLM_RESPONSES: int = int(os.getenv("CACHE_TTL_LLM_RESPONSES", "7200"))
    CACHE_TTL_PATCHES: int = int(os.getenv("CACHE_TTL_PATCHES", "86400"))

    # Celery Configuration
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
    
    # Output Configuration
    DEFAULT_OUTPUT_FORMAT: str = "table"
    SUPPORTED_FORMATS: list = ["table", "json", "csv", "sarif", "github", "markdown"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'
        extra = 'ignore'  # Ignore extra fields in .env

# Global settings instance
settings = Settings()

def validate_api_keys():
    """Validate that required API keys are present"""
    errors = []
    
    if not settings.OPENROUTER_API_KEY and not settings.GROQ_API_KEY and not settings.OPENAI_API_KEY:
        errors.append("❌ No API keys found! Set OPENROUTER_API_KEY, GROQ_API_KEY, or OPENAI_API_KEY")
    
    if settings.OPENROUTER_API_KEY and len(settings.OPENROUTER_API_KEY) < 10:
        errors.append("❌ OPENROUTER_API_KEY appears invalid (too short)")
    
    if settings.GROQ_API_KEY and len(settings.GROQ_API_KEY) < 10:
        errors.append("❌ GROQ_API_KEY appears invalid (too short)")
        
    if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith('sk-'):
        errors.append("❌ OPENAI_API_KEY appears invalid (should start with 'sk-')")
    
    if errors:
        print("\n".join(errors))
        print("\n📖 Get API keys from:")
        print("   • OpenRouter: https://openrouter.ai/")
        print("   • GroqCloud: https://console.groq.com/keys")
        print("   • OpenAI: https://platform.openai.com/api-keys")
        return False
    
    return True