from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional
from app.agents.security_agent import SecurityAgent
from app.services.llm_client import ModelType, get_available_models
from app.monitoring import MetricsMiddleware, metrics_endpoint, record_audit_metrics

app = FastAPI(
    title="AI Code Security Auditor",
    description="Automated security scanning and remediation for AI-generated code with multi-model LLM support",
    version="1.0.0"
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Remove global agent instance - create fresh ones per request

class AuditRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None
    model: Optional[str] = None  # Allow model selection
    use_advanced_analysis: Optional[bool] = False  # Enable advanced multi-model features
    
    @field_validator('code')
    @classmethod
    def code_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Code cannot be empty')
        return v
    
    @field_validator('language')
    @classmethod
    def language_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Language cannot be empty')
        valid_languages = ['python', 'javascript', 'java', 'go']
        if v.lower() not in valid_languages:
            raise ValueError(f'Language must be one of: {valid_languages}')
        return v.lower()
    
    @field_validator('model')
    @classmethod
    def model_must_be_valid(cls, v):
        if v is None:
            return v
        available_models = get_available_models()
        if v not in available_models:
            raise ValueError(f'Model must be one of: {available_models}')
        return v

class Vulnerability(BaseModel):
    id: str
    title: str
    description: str
    severity: str
    line_number: int
    cwe_id: str
    tool: str
    code_snippet: str

class RemediationSuggestion(BaseModel):
    vuln: Vulnerability
    recs: List[Dict[str, Any]]

class Patch(BaseModel):
    vuln: Vulnerability
    rec: Dict[str, Any]
    patch: Dict[str, Any]

class Assessment(BaseModel):
    vuln: Vulnerability
    rec: Dict[str, Any]
    patch: Dict[str, Any]
    assessment: Dict[str, Any]

class AuditResponse(BaseModel):
    scan_results: Dict[str, Any]
    vulnerabilities: List[Vulnerability]
    remediation_suggestions: List[RemediationSuggestion]
    patches: List[Patch]
    assessments: List[Assessment]
    model_info: Optional[Dict[str, Any]] = None  # Include model usage info

@app.post("/audit", response_model=AuditResponse)
async def audit_code(request: AuditRequest):
    """
    Audit code for security vulnerabilities with advanced multi-model LLM support
    
    - **code**: The code to analyze
    - **language**: Programming language (python, javascript, java, go)
    - **filename**: Optional filename for context
    - **model**: Optional specific model to use for LLM operations
    - **use_advanced_analysis**: Enable advanced multi-model features (classification, explanations)
    """
    try:
        # Create fresh agent instance per request
        agent = SecurityAgent()
        
        state = await agent.run(
            code=request.code,
            language=request.language,
            filename=request.filename or "",
            preferred_model=request.model,
            use_advanced_analysis=request.use_advanced_analysis
        )
        
        # Record metrics
        vulnerabilities = state.get("vulnerabilities", [])
        model = request.model or "agentica-org/deepcoder-14b-preview:free"
        record_audit_metrics(request.language, model, vulnerabilities)
        
        # Add model information to response
        model_info = None
        if hasattr(agent, 'llm_service') and hasattr(agent.llm_service, 'get_model_recommendations'):
            model_info = agent.llm_service.get_model_recommendations()
            
        return AuditResponse(
            scan_results=state["scan_results"],
            vulnerabilities=state["vulnerabilities"],
            remediation_suggestions=state["remediation_suggestions"],
            patches=state["patches"],
            assessments=state["assessments"],
            model_info=model_info
        )
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "1.0.0"}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return await metrics_endpoint()

@app.get("/models")
def get_models():
    """Get available LLM models and their recommended use cases"""
    return {
        "available_models": get_available_models(),
        "recommendations": {
            "code_patches": ModelType.DEEPCODER,
            "quality_assessment": ModelType.LLAMA, 
            "fast_classification": ModelType.QWEN,
            "security_explanations": ModelType.KIMI
        },
        "model_info": {
            ModelType.DEEPCODER: {
                "name": "DeepCoder 14B",
                "use_case": "Code patch generation and diffs",
                "strengths": ["Code understanding", "Precise diffs", "Security fixes"]
            },
            ModelType.KIMI: {
                "name": "Kimi Dev 72B", 
                "use_case": "Security explanations and education",
                "strengths": ["Clear explanations", "Educational content", "Detailed analysis"]
            },
            ModelType.QWEN: {
                "name": "Qwen 2.5 Coder 32B",
                "use_case": "Fast vulnerability classification", 
                "strengths": ["Speed", "Classification", "Triage decisions"]
            },
            ModelType.LLAMA: {
                "name": "LLaMA 3.3 70B",
                "use_case": "Balanced high-quality analysis",
                "strengths": ["Quality assessment", "Comprehensive review", "Balanced analysis"]
            }
        }
    }

@app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "message": "AI Code Security Auditor API",
        "version": "1.0.0", 
        "features": [
            "Multi-language security scanning (Python, JavaScript, Java, Go)",
            "AI-powered patch generation with DeepCoder",
            "Quality assessment with LLaMA 3.3",
            "Fast vulnerability classification with Qwen", 
            "Security explanations with Kimi",
            "RAG-enhanced remediation suggestions",
            "Secret detection and credential scanning",
            "Production monitoring and metrics"
        ],
        "endpoints": {
            "POST /audit": "Analyze code for security vulnerabilities",
            "GET /models": "List available LLM models",
            "GET /health": "Service health check",
            "GET /metrics": "Prometheus metrics"
        }
    }
