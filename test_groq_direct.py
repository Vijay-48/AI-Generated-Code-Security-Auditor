"""
Test Groq API directly to see what models are available
"""
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

async def test_groq_model(model_name):
    """Test a specific Groq model"""
    print(f"\n🧪 Testing Groq model: {model_name}")
    
    api_key = os.getenv("GROQ_API_KEY")
    base_url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": model_name,
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10,
        "temperature": 0.1
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(base_url, headers=headers, json=data, timeout=30.0)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"   ✅ SUCCESS: {content}")
                return True
            else:
                print(f"   ❌ FAILED: Status {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                return False
                
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:200]}")
        return False

async def main():
    print("=" * 60)
    print("🔍 Testing Groq Models Directly")
    print("=" * 60)
    
    # Test various model names
    test_models = [
        "compound",  # This is what groq/compound becomes
        "groq/compound",  # Full name
        "llama-3.1-8b-instant",  # Known working
        "llama-3.3-70b-versatile",  # Known working
        "gpt-oss-20b",  # Test if this exists in Groq
    ]
    
    for model in test_models:
        await test_groq_model(model)
    
    print("\n" + "=" * 60)
    print("💡 Note: If 'compound' fails, it means groq/compound")
    print("   should be routed to OpenRouter instead of Groq")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
