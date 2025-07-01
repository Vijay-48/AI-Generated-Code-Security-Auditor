import httpx
import json
import re
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

    async def generate_fix_diff(
        self, 
        vulnerable_code: str,
        vulnerability: Dict[str, Any],
        remediation_pattern: Dict[str, Any]
    ) -> Dict[str, Any]:
        system_prompt = (
            "You are a security engineer. Generate a git diff patch to fix the vulnerability. "
            "Return JSON with: {diff, explanation, confidence}"
        )
        
        user_prompt = (
            f"VULNERABLE CODE:\n```\n{vulnerable_code}\n```\n\n"
            f"VULNERABILITY: {vulnerability['title']} ({vulnerability['cwe_id']})\n"
            f"REMEDIATION PATTERN:\n{remediation_pattern['remediation_code']}\n\n"
            "Generate a git diff patch to fix this security vulnerability."
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,
                        "max_tokens": 1500
                    },
                    timeout=60.0
                )
                response.raise_for_status()
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                # Extract JSON from response
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                return {"diff": content, "explanation": "", "confidence": "MEDIUM"}
                
        except Exception as e:
            return {"error": str(e), "diff": "", "explanation": f"Error: {str(e)}"}

    async def assess_fix_quality(
        self, 
        original_code: str, 
        fixed_code: str, 
        vulnerability: Dict[str, Any]
    ) -> Dict[str, Any]:
        user_prompt = (
            f"Assess this fix for {vulnerability['title']} (CWE: {vulnerability['cwe_id']}):\n\n"
            f"ORIGINAL CODE:\n```\n{original_code}\n```\n\n"
            f"FIXED CODE:\n```\n{fixed_code}\n```\n\n"
            "Return JSON with scores (0-10) for: correctness, completeness, quality"
        )
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [{"role": "user", "content": user_prompt}],
                        "temperature": 0.1,
                        "max_tokens": 500
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                content = data['choices'][0]['message']['content']
                
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                return {"assessment": content}
                
        except Exception as e:
            return {"error": str(e)}