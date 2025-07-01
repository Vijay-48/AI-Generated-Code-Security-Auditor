from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
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

@app.post("/audit")
async def audit_code(request: AuditRequest):
    if not request.code or not request.language:
        raise HTTPException(status_code=400, detail="Code and language are required")
    
    try:
        return await agent.run(request.code, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)