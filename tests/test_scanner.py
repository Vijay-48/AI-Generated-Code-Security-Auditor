import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_python_scan(scanner):
    code = "import os\ndef insecure():\n    os.system('echo $USER')"
    results = await scanner.scan_code(code, "python")
    assert "vulnerabilities" in results
    assert len(results["vulnerabilities"]) > 0
    assert any(v["id"] == "B602" for v in results["vulnerabilities"])

@pytest.mark.asyncio
async def test_javascript_scan(scanner):
    code = "function insecure() {\n    eval('console.log(\"test\")');\n}"
    results = await scanner.scan_code(code, "javascript")
    assert "vulnerabilities" in results
    assert len(results["vulnerabilities"]) > 0

@pytest.mark.asyncio
async def test_unsupported_language(scanner):
    with pytest.raises(ValueError):
        await scanner.scan_code("code", "rust")

@patch("subprocess.run")
@pytest.mark.asyncio
async def test_scan_timeout(mock_run, scanner):
    mock_run.side_effect = TimeoutError("Scan timed out")
    code = "import os\nos.system('echo test')"
    results = await scanner.scan_code(code, "python")
    assert "error" in results
    assert "timeout" in results["error"].lower()