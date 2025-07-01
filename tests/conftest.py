import pytest
from app.config import settings
from app.services.scanner import SecurityScanner
from app.services.rag_service import RAGRemediationService
from app.services.llm_service import LLMService
from app.agents.security_agent import SecurityAgent

# Set test-specific environment variables
settings.OPENROUTER_API_KEY = "test-api-key"
settings.CHROMA_PERSIST_DIRECTORY = "./test_chroma_db"

@pytest.fixture(scope="module")
def scanner():
    return SecurityScanner()

@pytest.fixture(scope="module")
def rag_service():
    return RAGRemediationService(persist_directory="./test_chroma_db")

@pytest.fixture(scope="module")
def llm_service():
    return LLMService()

@pytest.fixture(scope="module")
def security_agent():
    return SecurityAgent()

@pytest.fixture(scope="function")
def sample_vulnerability():
    return {
        "id": "B602",
        "title": "Subprocess without shell equals true",
        "description": "Calling subprocess without shell=True is dangerous",
        "severity": "HIGH",
        "line_number": 5,
        "cwe_id": "CWE-78",
        "code_snippet": "import subprocess\nsubprocess.run(['ls', '-la'])"
    }