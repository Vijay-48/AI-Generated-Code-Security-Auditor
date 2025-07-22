from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from app.agents.security_agent import SecurityAgent
from app.services.llm_client import ModelType, get_available_models
from app.monitoring import MetricsMiddleware, metrics_endpoint, record_audit_metrics
from app.services.cache_service import init_cache, shutdown_cache, cache_service
from app.api.async_endpoints import async_router
from app.api.analytics_endpoints import analytics_router, initialize_analytics_service
from app.websocket_manager import websocket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle app startup and shutdown events"""
    # Startup
    print("🚀 Starting AI Code Security Auditor...")
    await init_cache()
    await websocket_manager.initialize()
    await initialize_analytics_service()
    print("✅ Application startup complete")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down AI Code Security Auditor...")
    await websocket_manager.shutdown()
    await shutdown_cache()
    print("✅ Application shutdown complete")


app = FastAPI(
    title="AI Code Security Auditor",
    description="Automated security scanning and remediation for AI-generated code with multi-model LLM support and async processing",
    version="2.0.0",
    lifespan=lifespan
)

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Include async endpoints
app.include_router(async_router)

# Include analytics endpoints  
app.include_router(analytics_router)

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
    cache_info: Optional[Dict[str, Any]] = None  # Include cache information

@app.post("/audit", response_model=AuditResponse)
async def audit_code(request: AuditRequest):
    """
    **LEGACY SYNC ENDPOINT** - For backward compatibility
    
    Audit code for security vulnerabilities with advanced multi-model LLM support.
    
    ⚠️  **Recommended**: Use `/async/audit` for better performance and progress tracking
    
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
        
        # **NEW: Store scan results in analytics database**
        try:
            from app.services.analytics_service import analytics_service
            import uuid
            
            scan_id = str(uuid.uuid4())
            metadata = {
                'language': request.language,
                'model': model,
                'scan_type': 'single_file',
                'files_scanned': 1,
                'file_path': request.filename or 'unknown'
            }
            
            # Ensure analytics service is connected
            if not analytics_service.engine:
                await analytics_service.connect()
            
            # Store the scan result
            await analytics_service.store_scan_result(scan_id, state, metadata)
            print(f"✅ Stored audit scan in analytics: {scan_id}")
            
        except Exception as e:
            print(f"⚠️ Failed to store audit in analytics: {e}")
            # Don't fail the request if analytics storage fails
        
        # Add model information to response
        model_info = None
        if hasattr(agent, 'llm_service') and hasattr(agent.llm_service, 'get_model_recommendations'):
            model_info = agent.llm_service.get_model_recommendations()
        
        # Add cache information
        cache_info = {
            "cache_available": cache_service.connected,
            "cache_status": "connected" if cache_service.connected else "disconnected",
            "recommendation": "Use /async/audit for caching benefits"
        }
            
        return AuditResponse(
            scan_results=state["scan_results"],
            vulnerabilities=state["vulnerabilities"],
            remediation_suggestions=state["remediation_suggestions"],
            patches=state["patches"],
            assessments=state["assessments"],
            model_info=model_info,
            cache_info=cache_info
        )
    except Exception as e:
        print(f"DEBUG: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Health check endpoint with cache status"""
    cache_status = "connected" if cache_service.connected else "disconnected"
    return {
        "status": "ok", 
        "version": "2.0.0",
        "features": ["async_processing", "caching", "websockets"],
        "cache_status": cache_status
    }

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
        "message": "AI Code Security Auditor API v2.0",
        "version": "2.0.0", 
        "features": [
            "Multi-language security scanning (Python, JavaScript, Java, Go)",
            "AI-powered patch generation with DeepCoder",
            "Quality assessment with LLaMA 3.3",
            "Fast vulnerability classification with Qwen", 
            "Security explanations with Kimi",
            "RAG-enhanced remediation suggestions",
            "Secret detection and credential scanning",
            "Production monitoring and metrics",
            "🚀 NEW: Async job processing with Redis caching",
            "🚀 NEW: Real-time progress tracking via WebSocket",
            "🚀 NEW: Smart caching for cost optimization",
            "🚀 PHASE 6: Bulk repository scanning with Git integration",
            "📊 PHASE 7: Advanced monitoring dashboards and analytics"
        ],
        "endpoints": {
            "POST /audit": "🔄 Legacy sync analysis (backward compatibility)",
            "POST /async/audit": "🚀 Async single-file analysis with job tracking",
            "POST /async/repo-scan": "🆕 PHASE 6: Bulk repository scanning",
            "GET /async/jobs/{job_id}/status": "📊 Get job status and progress",
            "GET /async/jobs/{job_id}/results": "📋 Get completed job results", 
            "WebSocket /async/jobs/{job_id}/ws": "⚡ Real-time progress updates",
            "GET /models": "List available LLM models",
            "GET /health": "Service health check with cache status",
            "GET /metrics": "Prometheus metrics",
            "GET /async/cache/stats": "Cache performance statistics",
            "GET /api/analytics/overview": "📊 PHASE 7: Complete dashboard analytics",
            "GET /api/analytics/metrics": "📊 Security metrics and KPIs", 
            "GET /api/analytics/trends": "📊 Vulnerability trends over time",
            "GET /api/analytics/repositories": "📊 Repository security rankings",
            "WebSocket /api/analytics/ws": "📊 Real-time analytics dashboard"
        },
        "phase_6_features": {
            "bulk_repository_scanning": {
                "description": "Enterprise-grade Git repository analysis",
                "features": [
                    "Git repository cloning and file discovery",
                    "Batch processing with configurable batch sizes",
                    "Real-time per-file progress tracking",
                    "File-level caching based on content hash", 
                    "Aggregated vulnerability reports",
                    "Support for custom include/exclude patterns",
                    "Repository metadata extraction",
                    "Multi-language detection and analysis"
                ],
                "endpoint": "POST /async/repo-scan",
                "example_request": {
                    "repository_url": "https://github.com/user/repo.git",
                    "branch": "main",
                    "max_files": 100,
                    "batch_size": 10,
                    "use_advanced_analysis": True,
                    "include_patterns": ["*.py", "*.js", "*.java"],
                    "exclude_patterns": ["*/tests/*", "*/node_modules/*"]
                }
            }
        },
        "migration_guide": {
            "from_sync_to_async": {
                "old": "POST /audit",
                "new": "POST /async/audit", 
                "benefits": ["No timeouts", "Progress tracking", "Caching", "Better performance"]
            },
            "single_file_to_bulk": {
                "old": "POST /async/audit",
                "new": "POST /async/repo-scan",
                "benefits": ["Entire repository analysis", "Batch processing", "Aggregated reports", "Git integration"]
            }
        }
    }
