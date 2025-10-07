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
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_REFERER: str = "https://ai-code-security-auditor.com"
    OPENROUTER_TITLE: str = "AI Code Security Auditor"
    
    # OpenAI API Configuration  
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # Available Models Configuration
    DEFAULT_MODEL: str = "openai/gpt-4"
    AVAILABLE_MODELS: dict = {
        "openai/gpt-4": "OpenAI GPT-4 - Best overall analysis",
        "openai/gpt-3.5-turbo": "OpenAI GPT-3.5 Turbo - Fast and efficient", 
        "agentica-org/deepcoder-14b-preview:free": "DeepCoder - Code patches",
        "meta-llama/llama-3.3-70b-instruct:free": "LLaMA 3.3 - Quality assessment",
        "qwen/qwen-2.5-coder-32b-instruct:free": "Qwen - Fast classification",
        "moonshotai/kimi-dev-72b:free": "Kimi - Security explanations"
    }
    
    # Security Scanner Configuration
    SUPPORTED_LANGUAGES: list = ["python", "javascript", "java", "go", "typescript"]
    MAX_FILE_SIZE_MB: int = 10
    SCAN_TIMEOUT_SECONDS: int = 300
    
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
    
    if not settings.OPENROUTER_API_KEY and not settings.OPENAI_API_KEY:
        errors.append("❌ No API keys found! Set OPENROUTER_API_KEY or OPENAI_API_KEY")
    
    if settings.OPENROUTER_API_KEY and len(settings.OPENROUTER_API_KEY) < 10:
        errors.append("❌ OPENROUTER_API_KEY appears invalid (too short)")
        
    if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith('sk-'):
        errors.append("❌ OPENAI_API_KEY appears invalid (should start with 'sk-')")
    
    if errors:
        print("\n".join(errors))
        print("\n📖 Get API keys from:")
        print("   • OpenRouter: https://openrouter.ai/")  
        print("   • OpenAI: https://platform.openai.com/api-keys")
        return False
    
    return True