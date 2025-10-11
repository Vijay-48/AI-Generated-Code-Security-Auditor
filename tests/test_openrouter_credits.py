"""
Test OpenRouter API key and credits
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_openrouter_key():
    """Test OpenRouter API key"""
    print("🔍 Testing OpenRouter API Key...")
    
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        print("❌ No OPENROUTER_API_KEY found in .env")
        return
    
    print(f"✅ API Key found: {api_key[:15]}...")
    
    # Test with a simple model
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:8000",
        "X-Title": "AI Code Security Auditor",
        "Content-Type": "application/json"
    }
    
    # Try a free model first
    free_models = [
        "meta-llama/llama-3.2-3b-instruct:free",
        "qwen/qwen-2.5-coder-32b-instruct:free",
    ]
    
    for model in free_models:
        print(f"\n🧪 Testing free model: {model}")
        
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Say hi"}],
            "max_tokens": 5
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"   ✅ SUCCESS: {content}")
                    return True
                else:
                    print(f"   ❌ FAILED: Status {response.status_code}")
                    print(f"   Response: {response.text[:300]}")
                    
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)[:200]}")
    
    return False

if __name__ == "__main__":
    asyncio.run(test_openrouter_key())
