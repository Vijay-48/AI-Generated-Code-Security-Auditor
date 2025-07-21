import os
import requests
import json
from app.config import settings

class ModelType:
    """Recommended models for different use cases"""
    DEEPCODER = "agentica-org/deepcoder-14b-preview:free"  # Code patch generation
    KIMI = "moonshotai/kimi-dev-72b:free"                  # Security explanations  
    QWEN = "qwen/qwen-2.5-coder-32b-instruct:free"        # Fast vulnerability classification
    LLAMA = "meta-llama/llama-3.3-70b-instruct:free"      # High quality, balanced performance

def get_available_models():
    """Get list of available OpenRouter models from config"""
    return [model.strip() for model in settings.OPENROUTER_MODELS.split(",")]

def query_openrouter(prompt: str, model: str = ModelType.DEEPCODER, max_tokens: int = 2000, temperature: float = 0.1):
    """
    Query OpenRouter API with specified model
    
    Args:
        prompt: The prompt to send to the model
        model: Model to use (default: DeepCoder for code generation)
        max_tokens: Maximum tokens to generate
        temperature: Generation temperature
        
    Returns:
        str: Generated response content
    """
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")
        
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_REFERER,
        "X-Title": settings.OPENROUTER_TITLE
    }

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(settings.OPENROUTER_BASE_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def query_openrouter_with_messages(messages: list, model: str = ModelType.DEEPCODER, max_tokens: int = 2000, temperature: float = 0.1):
    """
    Query OpenRouter API with custom message structure
    
    Args:
        messages: List of message dictionaries with role and content
        model: Model to use (default: DeepCoder for code generation)
        max_tokens: Maximum tokens to generate
        temperature: Generation temperature
        
    Returns:
        str: Generated response content
    """
    if not settings.OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY not configured")
        
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_REFERER,
        "X-Title": settings.OPENROUTER_TITLE
    }

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature
    }

    response = requests.post(settings.OPENROUTER_BASE_URL, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def generate_fix(code: str, vuln_desc: str, model: str = ModelType.DEEPCODER):
    """
    Generate a security fix for vulnerable code
    
    Args:
        code: The vulnerable code
        vuln_desc: Description of the vulnerability  
        model: Model to use for generation
        
    Returns:
        str: Generated fix with diff and explanation
    """
    prompt = f"""
    You are a secure code assistant. Given the following insecure code:
    
    ```python
    {code}
    ```

    Detected issue: {vuln_desc}

    Generate a safe replacement patch. Return only the diff and a short explanation.
    Format as JSON:
    {{
        "diff": "... actual git diff ...",
        "explanation": "Brief explanation of the fix",
        "confidence": "HIGH/MEDIUM/LOW",
        "potential_issues": ["list", "of", "issues"],
        "additional_recommendations": ["list", "of", "recommendations"]
    }}
    """

    return query_openrouter(prompt, model)

def assess_fix_quality(original_code: str, fixed_code: str, vuln_desc: str, model: str = ModelType.LLAMA):
    """
    Assess the quality of a security fix
    
    Args:
        original_code: Original vulnerable code
        fixed_code: Fixed code
        vuln_desc: Vulnerability description
        model: Model to use for assessment
        
    Returns:
        str: Quality assessment in JSON format
    """
    prompt = f"""
    Rate this security fix for the vulnerability: {vuln_desc}
    
    ORIGINAL CODE:
    ```
    {original_code}
    ```
    
    FIXED CODE:
    ```
    {fixed_code}
    ```
    
    Provide a comprehensive assessment in JSON format:
    {{
        "overall_score": 85,
        "correctness": "HIGH/MEDIUM/LOW",
        "completeness": "Assessment of completeness",
        "code_quality": "Assessment of code quality",
        "performance_impact": "Assessment of performance impact",
        "issues_found": ["list", "of", "issues"],
        "recommendations": ["list", "of", "recommendations"]
    }}
    """
    
    return query_openrouter(prompt, model)

def classify_vulnerability(code: str, vuln_info: dict, model: str = ModelType.QWEN):
    """
    Fast vulnerability classification and severity assessment
    
    Args:
        code: Code snippet with vulnerability
        vuln_info: Vulnerability information dictionary
        model: Model to use (default: Qwen for fast classification)
        
    Returns:
        str: Classification results
    """
    prompt = f"""
    Classify this security vulnerability quickly:
    
    CODE:
    ```
    {code}
    ```
    
    VULNERABILITY INFO:
    - ID: {vuln_info.get('id', 'Unknown')}
    - Title: {vuln_info.get('title', 'Unknown')}
    - Severity: {vuln_info.get('severity', 'Unknown')}
    
    Provide fast classification:
    {{
        "true_severity": "CRITICAL/HIGH/MEDIUM/LOW",
        "category": "injection/xss/auth/crypto/etc",
        "exploitability": "HIGH/MEDIUM/LOW",
        "priority": "URGENT/HIGH/MEDIUM/LOW"
    }}
    """
    
    return query_openrouter(prompt, model)

def explain_vulnerability(code: str, vuln_info: dict, model: str = ModelType.KIMI):
    """
    Generate detailed security explanation
    
    Args:
        code: Code snippet with vulnerability
        vuln_info: Vulnerability information dictionary  
        model: Model to use (default: Kimi for explanations)
        
    Returns:
        str: Detailed explanation
    """
    prompt = f"""
    Provide a detailed security explanation for developers:
    
    VULNERABLE CODE:
    ```
    {code}
    ```
    
    DETECTED ISSUE:
    - ID: {vuln_info.get('id', 'Unknown')}
    - Title: {vuln_info.get('title', 'Unknown')}
    - Description: {vuln_info.get('description', 'No description')}
    
    Explain in developer-friendly terms:
    1. What exactly is the security risk?
    2. How could this be exploited?
    3. What are the potential impacts?
    4. Best practices to prevent this in the future?
    
    Format as clear, educational explanation.
    """
    
    return query_openrouter(prompt, model)