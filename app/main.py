from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from app.agents.security_agent import SecurityAgent

app = FastAPI(
    title="AI Code Security Auditor",
    description="Automated security scanning and remediation for AI-generated code",
    version="1.0.0"
)
agent = SecurityAgent()

class AuditRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None

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

@app.post("/audit", response_model=AuditResponse)
async def audit_code(request: AuditRequest):
    try:
        state = await agent.run(
            code=request.code,
            language=request.language,
            filename=request.filename or ""
        )
        return AuditResponse(
            scan_results=state["scan_results"],
            vulnerabilities=state["vulnerabilities"],
            remediation_suggestions=state["remediation_suggestions"],
            patches=state["patches"],
            assessments=state["assessments"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}