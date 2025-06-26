import json
import re
import httpx
from app.config import settings

class LLMService:
    def __init__(self):
        self.model = "deepseek/deepseek-r1:free"
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.OPENROUTER_REFERER,
            "X-Title": settings.OPENROUTER_TITLE
        }

    async def _call_openrouter(self, messages, max_tokens, temperature):
        async with httpx.AsyncClient() as client:
            data = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()

    async def generate_fix_diff(self, vulnerable_code, vulnerability, remediation_pattern):
        system_prompt = """You are an expert security engineer who generates precise git diff patches to fix security vulnerabilities."""
        
        user_prompt = (
            f"VULNERABLE CODE:\n```\n{vulnerable_code}\n```\n"
            f"VULNERABILITY: {vulnerability['title']} ({vulnerability['cwe_id']})\n"
            f"PATTERN:\n{remediation_pattern['remediation_code']}\n"
            "Generate a git diff patch to fix this security vulnerability.\n"
            "Return JSON: {diff, explanation, confidence, potential_issues, additional_recommendations}"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_openrouter(
                messages, max_tokens=2000, temperature=0.1
            )
            content = response['choices'][0]['message']['content']
            return self._parse_response(content)
        except Exception as e:
            return {
                "error": str(e),
                "diff": "",
                "explanation": f"Error generating fix: {str(e)}",
                "confidence": "LOW",
                "potential_issues": ["LLM generation failed"],
                "additional_recommendations": ["Manual review required"]
            }

    async def assess_fix_quality(self, original_code, fixed_code, vulnerability):
        user_prompt = (
            f"Rate this fix for {vulnerability['title']} (CWE: {vulnerability['cwe_id']}):\n"
            f"ORIGINAL:\n```\n{original_code}\n```\n"
            f"FIXED:\n```\n{fixed_code}\n```\n"
            "Return JSON with these keys: "
            "overall_score, correctness, completeness, code_quality, performance_impact, issues_found, recommendations"
        )
        
        messages = [{"role": "user", "content": user_prompt}]
        
        try:
            response = await self._call_openrouter(
                messages, max_tokens=800, temperature=0.1
            )
            content = response['choices'][0]['message']['content']
            return self._parse_json(content)
        except Exception as e:
            return {"error": f"Error assessing fix: {str(e)}"}

    def _parse_response(self, content: str) -> dict:
        """Parse LLM response and extract JSON"""
        try:
            # Look for JSON in code blocks
            json_match = re.search(r'```json\n({.*?})\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Look for JSON without code blocks
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Fallback if JSON parsing fails
            return {
                "diff": content,
                "explanation": "Generated diff patch",
                "confidence": "MEDIUM",
                "potential_issues": [],
                "additional_recommendations": []
            }
        except json.JSONDecodeError:
            return {
                "diff": content,
                "explanation": "Generated diff patch",
                "confidence": "MEDIUM",
                "potential_issues": ["JSON parsing failed"],
                "additional_recommendations": ["Verify diff manually"]
            }

    def _parse_json(self, content: str) -> dict:
        """Parse JSON response from assessment"""
        try:
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"error": "Could not parse assessment response"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format in assessment response"}