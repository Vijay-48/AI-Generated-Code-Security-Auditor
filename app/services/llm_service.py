import json
import re
import httpx
from app.config import settings
from app.services.llm_client import ModelType, query_openrouter_with_messages, generate_fix, assess_fix_quality

class LLMService:
    def __init__(self):
        # Default models for different use cases
        self.patch_model = ModelType.DEEPCODER  # Best for code generation
        self.assessment_model = ModelType.LLAMA  # Best for quality assessment
        self.classification_model = ModelType.QWEN  # Fast classification
        self.explanation_model = ModelType.KIMI  # Best explanations
        
        self.base_url = settings.OPENROUTER_BASE_URL.replace("/chat/completions", "")
        self.headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.OPENROUTER_REFERER,
            "X-Title": settings.OPENROUTER_TITLE
        }

    async def _call_openrouter(self, messages, max_tokens, temperature, model=None):
        """Legacy method for backward compatibility - now uses httpx for async"""
        if model is None:
            model = self.patch_model
            
        async with httpx.AsyncClient() as client:
            data = {
                "model": model,
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
        """Generate security fix using DeepCoder model optimized for code patches"""
        system_prompt = """You are an expert security engineer who generates precise git diff patches to fix security vulnerabilities. Use the DeepCoder model's advanced code understanding to create accurate, minimal diffs."""
        
        user_prompt = (
            f"VULNERABLE CODE:\n```\n{vulnerable_code}\n```\n"
            f"VULNERABILITY: {vulnerability['title']} ({vulnerability['cwe_id']})\n"
            f"REMEDIATION PATTERN:\n{remediation_pattern['remediation_code']}\n"
            "Generate a git diff patch to fix this security vulnerability.\n"
            "Return JSON: {{\"diff\": \"...\", \"explanation\": \"...\", \"confidence\": \"HIGH/MEDIUM/LOW\", \"potential_issues\": [], \"additional_recommendations\": []}}"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Use DeepCoder model for optimal code generation
            response = await self._call_openrouter(
                messages, max_tokens=2000, temperature=0.1, model=self.patch_model
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
        """Assess fix quality using LLaMA model for balanced, high-quality analysis"""
        system_prompt = "You are a senior security architect performing code review. Provide comprehensive quality assessment."
        
        user_prompt = (
            f"Rate this security fix for {vulnerability['title']} (CWE: {vulnerability['cwe_id']}):\n"
            f"ORIGINAL:\n```\n{original_code}\n```\n"
            f"FIXED:\n```\n{fixed_code}\n```\n"
            "Return JSON with these keys: "
            "{{\"overall_score\": 85, \"correctness\": \"HIGH/MEDIUM/LOW\", \"completeness\": \"...\", \"code_quality\": \"...\", \"performance_impact\": \"...\", \"issues_found\": [], \"recommendations\": []}}"
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            # Use LLaMA for balanced quality assessment
            response = await self._call_openrouter(
                messages, max_tokens=800, temperature=0.1, model=self.assessment_model
            )
            content = response['choices'][0]['message']['content']
            return self._parse_json(content)
        except Exception as e:
            return {"error": f"Error assessing fix: {str(e)}"}

    async def classify_vulnerability_fast(self, code_snippet, vulnerability):
        """Fast vulnerability classification using Qwen model"""
        user_prompt = (
            f"Quickly classify this vulnerability:\n"
            f"CODE:\n```\n{code_snippet}\n```\n"
            f"ISSUE: {vulnerability['title']} ({vulnerability['id']})\n"
            f"CURRENT SEVERITY: {vulnerability['severity']}\n"
            "Return JSON: {{\"true_severity\": \"CRITICAL/HIGH/MEDIUM/LOW\", \"category\": \"...\", \"exploitability\": \"HIGH/MEDIUM/LOW\", \"priority\": \"URGENT/HIGH/MEDIUM/LOW\"}}"
        )
        
        try:
            # Use Qwen for fast classification
            response = await self._call_openrouter(
                [{"role": "user", "content": user_prompt}], 
                max_tokens=300, temperature=0.1, model=self.classification_model
            )
            content = response['choices'][0]['message']['content']
            return self._parse_json(content)
        except Exception as e:
            return {"error": f"Error classifying vulnerability: {str(e)}"}

    async def explain_vulnerability(self, code_snippet, vulnerability):
        """Generate detailed security explanation using Kimi model"""
        user_prompt = (
            f"Explain this security vulnerability in detail for developers:\n"
            f"CODE:\n```\n{code_snippet}\n```\n"
            f"VULNERABILITY: {vulnerability['title']}\n"
            f"DESCRIPTION: {vulnerability.get('description', 'No description')}\n"
            "Explain:\n1. What is the security risk?\n2. How could this be exploited?\n"
            "3. What are potential impacts?\n4. Best practices to prevent this?\n"
            "Provide clear, educational explanation."
        )
        
        try:
            # Use Kimi for detailed explanations
            response = await self._call_openrouter(
                [{"role": "user", "content": user_prompt}], 
                max_tokens=1000, temperature=0.2, model=self.explanation_model
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

    def get_model_recommendations(self):
        """Return current model configuration and recommendations"""
        return {
            "patch_generation": self.patch_model,
            "quality_assessment": self.assessment_model, 
            "fast_classification": self.classification_model,
            "explanations": self.explanation_model,
            "recommendations": {
                "code_patches": "DeepCoder - Optimized for code generation and diffs",
                "quality_review": "LLaMA 3.3 - Balanced, high-quality analysis",
                "fast_triage": "Qwen - Fast vulnerability classification",
                "security_education": "Kimi - Detailed explanations and guidance"
            }
        }

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
