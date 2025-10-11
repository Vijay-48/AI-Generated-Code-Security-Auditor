import json
import re
import httpx
import openai
from typing import Optional, Dict, Any
from app.config import settings

class LLMService:
    def __init__(self):
        # Model configuration from settings
        self.patch_model = settings.MODEL_PATCH_GENERATION
        self.patch_model_secondary = settings.MODEL_PATCH_GENERATION_SECONDARY
        self.assessment_model = settings.MODEL_QUALITY_ASSESSMENT
        self.assessment_model_secondary = settings.MODEL_QUALITY_ASSESSMENT_SECONDARY
        self.classification_model = settings.MODEL_FAST_CLASSIFICATION
        self.classification_model_secondary = settings.MODEL_FAST_CLASSIFICATION_SECONDARY
        self.explanation_model = settings.MODEL_DETAILED_EXPLANATION
        self.explanation_model_secondary = settings.MODEL_DETAILED_EXPLANATION_SECONDARY
        
        # OpenRouter configuration
        self.openrouter_headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": settings.OPENROUTER_REFERER,
            "X-Title": settings.OPENROUTER_TITLE,
            "Content-Type": "application/json"
        }
        
        # GroqCloud configuration
        self.groq_headers = {
            "Authorization": f"Bearer {settings.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # OpenAI configuration
        if settings.OPENAI_API_KEY:
            openai.api_key = settings.OPENAI_API_KEY

    async def _call_openai_direct(self, messages: list, model: str = "gpt-4", max_tokens: int = 2000, temperature: float = 0.1) -> Dict[str, Any]:
        """Call OpenAI API directly"""
        try:
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content
                    }
                }]
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    async def _call_openrouter(self, messages: list, model: str, max_tokens: int = 2000, temperature: float = 0.1) -> Dict[str, Any]:
        """Call OpenRouter API for multi-model access"""
        try:
            async with httpx.AsyncClient() as client:
                data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                response = await client.post(
                    settings.OPENROUTER_BASE_URL,
                    headers=self.openrouter_headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"OpenRouter API error: {str(e)}")

    async def _call_groq(self, messages: list, model: str, max_tokens: int = 2000, temperature: float = 0.1) -> Dict[str, Any]:
        """Call GroqCloud API for fast inference"""
        try:
            async with httpx.AsyncClient() as client:
                # Remove provider prefix for Groq models
                groq_model = model.replace("groq/", "")
                
                data = {
                    "model": groq_model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature
                }
                response = await client.post(
                    settings.GROQ_BASE_URL,
                    headers=self.groq_headers,
                    json=data,
                    timeout=60.0
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            raise Exception(f"GroqCloud API error: {str(e)}")

    async def _call_llm(self, messages: list, model: str, max_tokens: int = 2000, temperature: float = 0.1, use_fallback: bool = False) -> Dict[str, Any]:
        """Smart LLM caller - routes to appropriate API based on model and available keys"""
        
        # Determine which provider to use based on model prefix or name
        is_groq_model = (
            model.startswith("groq/") or 
            model.startswith("llama-3.1") or 
            model.startswith("llama-3.3") or
            "gpt-oss" in model
        )
        
        is_openrouter_model = (
            "qwen" in model.lower() or
            "mistral" in model.lower() or
            "deepseek" in model.lower() or
            "kimi" in model.lower() or
            "nemotron" in model.lower() or
            "glm" in model.lower() or
            model.startswith("meta-llama/") or
            model.startswith("nvidia/")
        )
        
        try:
            # Route to GroqCloud for Groq models
            if is_groq_model and settings.GROQ_API_KEY:
                return await self._call_groq(messages, model, max_tokens, temperature)
            
            # Route to OpenRouter for OpenRouter models
            elif is_openrouter_model and settings.OPENROUTER_API_KEY:
                return await self._call_openrouter(messages, model, max_tokens, temperature)
            
            # If it's an OpenAI model and we have OpenAI API key, use direct API
            elif model.startswith("openai/") and settings.OPENAI_API_KEY:
                openai_model = model.replace("openai/", "")
                return await self._call_openai_direct(messages, openai_model, max_tokens, temperature)
            
            # Fallback to OpenRouter if available
            elif settings.OPENROUTER_API_KEY:
                return await self._call_openrouter(messages, model, max_tokens, temperature)
            
            # Fallback to Groq if available
            elif settings.GROQ_API_KEY:
                return await self._call_groq(messages, model, max_tokens, temperature)
            
            else:
                raise Exception("No API keys available. Set GROQ_API_KEY, OPENROUTER_API_KEY, or OPENAI_API_KEY")
                
        except Exception as e:
            # If primary model fails and we haven't tried fallback yet, try secondary model
            if not use_fallback:
                # Map to secondary models
                secondary_model = self._get_secondary_model(model)
                if secondary_model and secondary_model != model:
                    print(f"⚠️  Primary model {model} failed, trying fallback {secondary_model}")
                    return await self._call_llm(messages, secondary_model, max_tokens, temperature, use_fallback=True)
            raise e
    
    def _get_secondary_model(self, primary_model: str) -> Optional[str]:
        """Get secondary/fallback model for a given primary model"""
        model_fallback_map = {
            self.patch_model: self.patch_model_secondary,
            self.assessment_model: self.assessment_model_secondary,
            self.classification_model: self.classification_model_secondary,
            self.explanation_model: self.explanation_model_secondary
        }
        return model_fallback_map.get(primary_model, None)

    async def generate_fix_diff(self, vulnerable_code: str, vulnerability: Dict[str, Any], remediation_pattern: Dict[str, Any]) -> Dict[str, Any]:
        """Generate security fix using AI (prefers GPT-4 for best results)"""
        
        system_prompt = """You are an expert security engineer who generates precise git diff patches to fix security vulnerabilities. 
        Focus on creating minimal, effective changes that resolve the security issue without breaking functionality."""
        
        user_prompt = (
            f"VULNERABLE CODE:\n```\n{vulnerable_code}\n```\n\n"
            f"VULNERABILITY: {vulnerability.get('title', 'Unknown')} ({vulnerability.get('cwe_id', 'Unknown')})\n"
            f"DESCRIPTION: {vulnerability.get('description', 'No description')}\n"
            f"SEVERITY: {vulnerability.get('severity', 'Unknown')}\n\n"
            f"REMEDIATION GUIDANCE:\n{remediation_pattern.get('remediation_code', 'Use secure coding practices')}\n\n"
            "Generate a secure fix for this code. Return your response as JSON with these keys:\n"
            '{"diff": "git diff format patch", "explanation": "clear explanation of the fix", "confidence": "HIGH/MEDIUM/LOW", "potential_issues": ["list of potential issues"], "additional_recommendations": ["extra security suggestions"]}'
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_llm(messages, self.patch_model, max_tokens=2000, temperature=0.1)
            content = response['choices'][0]['message']['content']
            return self._parse_json_response(content)
        except Exception as e:
            return {
                "error": str(e),
                "diff": "",
                "explanation": f"Error generating fix: {str(e)}",
                "confidence": "LOW",
                "potential_issues": ["LLM generation failed"],
                "additional_recommendations": ["Manual review required"]
            }

    async def assess_fix_quality(self, original_code: str, fixed_code: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Assess fix quality using AI"""
        
        system_prompt = "You are a senior security architect performing code review. Provide comprehensive quality assessment."
        
        user_prompt = (
            f"Rate this security fix for {vulnerability.get('title', 'Unknown')} (CWE: {vulnerability.get('cwe_id', 'Unknown')}):\n\n"
            f"ORIGINAL CODE:\n```\n{original_code}\n```\n\n"
            f"FIXED CODE:\n```\n{fixed_code}\n```\n\n"
            "Evaluate the fix and return JSON with these keys: "
            '{"overall_score": 85, "correctness": "HIGH/MEDIUM/LOW", "completeness": "description", "code_quality": "description", "performance_impact": "description", "issues_found": ["list"], "recommendations": ["list"]}'
        )
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        try:
            response = await self._call_llm(messages, self.assessment_model, max_tokens=800, temperature=0.1)
            content = response['choices'][0]['message']['content']
            return self._parse_json_response(content)
        except Exception as e:
            return {"error": f"Error assessing fix: {str(e)}"}

    async def classify_vulnerability_fast(self, code_snippet: str, vulnerability: Dict[str, Any]) -> Dict[str, Any]:
        """Fast vulnerability classification using efficient model"""
        
        user_prompt = (
            f"Quickly classify this security vulnerability:\n\n"
            f"CODE:\n```\n{code_snippet}\n```\n\n"
            f"ISSUE: {vulnerability.get('title', 'Unknown')} ({vulnerability.get('id', 'Unknown')})\n"
            f"CURRENT SEVERITY: {vulnerability.get('severity', 'Unknown')}\n\n"
            "Return JSON: "
            '{"true_severity": "CRITICAL/HIGH/MEDIUM/LOW", "category": "vulnerability category", "exploitability": "HIGH/MEDIUM/LOW", "priority": "URGENT/HIGH/MEDIUM/LOW", "reasoning": "brief explanation"}'
        )
        
        try:
            response = await self._call_llm(
                [{"role": "user", "content": user_prompt}], 
                self.classification_model, 
                max_tokens=300, 
                temperature=0.1
            )
            content = response['choices'][0]['message']['content']
            return self._parse_json_response(content)
        except Exception as e:
            return {"error": f"Error classifying vulnerability: {str(e)}"}

    async def explain_vulnerability(self, code_snippet: str, vulnerability: Dict[str, Any]) -> str:
        """Generate detailed security explanation using AI"""
        
        user_prompt = (
            f"Explain this security vulnerability in detail for developers:\n\n"
            f"CODE:\n```\n{code_snippet}\n```\n\n"
            f"VULNERABILITY: {vulnerability.get('title', 'Unknown')}\n"
            f"DESCRIPTION: {vulnerability.get('description', 'No description')}\n"
            f"SEVERITY: {vulnerability.get('severity', 'Unknown')}\n\n"
            "Provide a comprehensive explanation covering:\n"
            "1. What is the security risk?\n"
            "2. How could this be exploited?\n"
            "3. What are the potential impacts?\n"
            "4. Best practices to prevent this vulnerability?\n\n"
            "Make it educational and easy to understand for developers."
        )
        
        try:
            response = await self._call_llm(
                [{"role": "user", "content": user_prompt}], 
                self.explanation_model, 
                max_tokens=1000, 
                temperature=0.2
            )
            return response['choices'][0]['message']['content']
        except Exception as e:
            return f"Error generating explanation: {str(e)}"

    def get_model_recommendations(self) -> Dict[str, Any]:
        """Return current model configuration and recommendations"""
        return {
            "patch_generation": self.patch_model,
            "quality_assessment": self.assessment_model, 
            "fast_classification": self.classification_model,
            "explanations": self.explanation_model,
            "available_models": settings.AVAILABLE_MODELS,
            "recommendations": {
                "best_quality": "openai/gpt-4 - Highest quality analysis and fixes",
                "cost_effective": "openai/gpt-3.5-turbo - Good quality, lower cost",
                "free_options": "Use OpenRouter free models for testing"
            },
            "api_status": {
                "openai_available": bool(settings.OPENAI_API_KEY),
                "openrouter_available": bool(settings.OPENROUTER_API_KEY)
            }
        }

    def _parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM, handling various formats"""
        try:
            # Look for JSON in code blocks
            json_match = re.search(r'```json\n({.*?})\n```', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
            
            # Look for JSON without code blocks
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # If no JSON found, return the content as explanation
            return {
                "explanation": content,
                "confidence": "MEDIUM",
                "potential_issues": [],
                "additional_recommendations": []
            }
            
        except json.JSONDecodeError:
            return {
                "explanation": content,
                "confidence": "MEDIUM", 
                "potential_issues": ["JSON parsing failed"],
                "additional_recommendations": ["Manual review recommended"]
            }