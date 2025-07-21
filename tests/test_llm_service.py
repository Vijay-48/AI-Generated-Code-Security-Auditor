import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_generate_fix_diff(llm_service, sample_vulnerability):
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": '{"diff": "test diff", "explanation": "test"}'}}]
        }
        
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
    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value.json.return_value = {
            "choices": [{"message": {"content": '{"overall_score": 8}'}}]
        }
        
        result = await llm_service.assess_fix_quality(
            "original code",
            "fixed code",
            sample_vulnerability
        )
        
        assert "overall_score" in result
        assert result["overall_score"] == 8