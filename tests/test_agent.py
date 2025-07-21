import pytest
from unittest.mock import patch, AsyncMock

@pytest.mark.asyncio
async def test_agent_full_flow(security_agent):
    code = "import os\ndef insecure():\n    os.system('echo $USER')"
    state = await security_agent.run(code, "python")
    
    assert "scan_results" in state
    assert "vulnerabilities" in state
    assert "remediation_suggestions" in state
    assert "patches" in state
    assert "assessments" in state
    
    assert len(state["vulnerabilities"]) > 0
    assert len(state["remediation_suggestions"]) > 0
    assert len(state["patches"]) > 0
    assert len(state["assessments"]) > 0

@pytest.mark.asyncio
async def test_agent_with_scan_error(security_agent):
    with patch("app.services.scanner.SecurityScanner.scan_code", 
               new_callable=AsyncMock) as mock_scan:
        mock_scan.return_value = {"error": "Scan failed"}
        
        state = await security_agent.run("code", "python")
        assert "error" in state["scan_results"]
        assert len(state["vulnerabilities"]) == 0