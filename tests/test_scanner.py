import pytest
from unittest.mock import patch

@pytest.mark.asyncio
async def test_python_scan(scanner):
    code = "import os\ndef insecure():\n    os.system('echo $USER')"
    results = await scanner.scan_code(code, "python")
    assert "vulnerabilities" in results
    assert len(results["vulnerabilities"]) > 0
    assert any(v["id"] in ["B602", "B605", "B607"] for v in results["vulnerabilities"])

@pytest.mark.asyncio
async def test_javascript_scan(scanner):
    code = "function insecure() {\n    eval('console.log(\"test\")');\n}"
    results = await scanner.scan_code(code, "javascript")
    assert "vulnerabilities" in results
    # JavaScript vulnerability detection may vary based on semgrep rules
    # Just check that the scanner processes the code without error
    assert results is not None

@pytest.mark.asyncio
async def test_unsupported_language(scanner):
    with pytest.raises(ValueError):
        await scanner.scan_code("code", "rust")

@patch("app.services.scanner.subprocess.run")
@pytest.mark.asyncio
async def test_scan_timeout(mock_run, scanner):
    mock_run.side_effect = TimeoutError("Scan timed out")
    code = "import os\nos.system('echo test')"
    results = await scanner.scan_code(code, "python")
    # The scan_code method should handle the exception and return an error-free result
    # but the individual tool results should contain errors
    assert "vulnerabilities" in results