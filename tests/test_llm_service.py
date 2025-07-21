import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_generate_fix_diff(llm_service, sample_vulnerability):
    # Mock the response object properly
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"diff": "test diff", "explanation": "test"}'}}]
    }
    mock_response.raise_for_status.return_value = None

    # Mock the client context manager
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        remediation_pattern = {
            "remediation_code": "# Safe code pattern",
            "metadata": {"cwe": "CWE-78"}
        }
        
        result = await llm_service.generate_fix_diff(
            sample_vulnerability["code_snippet"],
            sample_vulnerability,
            remediation_pattern
        )
        
        assert "diff" in result
        assert result["diff"] == "test diff"

@pytest.mark.asyncio
async def test_assess_fix_quality(llm_service, sample_vulnerability):
    # Mock the response object properly
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": '{"overall_score": 8}'}}]
    }
    mock_response.raise_for_status.return_value = None

    # Mock the client context manager
    mock_client = AsyncMock()
    mock_client.__aenter__.return_value.post.return_value = mock_response
    
    with patch("httpx.AsyncClient", return_value=mock_client):
        result = await llm_service.assess_fix_quality(
            "original code",
            "fixed code",
            sample_vulnerability
        )
        
        assert "overall_score" in result
        assert result["overall_score"] == 8