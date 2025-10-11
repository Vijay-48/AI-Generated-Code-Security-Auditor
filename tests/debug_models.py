"""
Debug script to test model calls directly
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.services.llm_service import LLMService
from app.config import settings

async def test_model_call(model_name):
    """Test a specific model"""
    print(f"\n🧪 Testing {model_name}...")
    
    llm = LLMService()
    
    try:
        messages = [{"role": "user", "content": "Say 'hello' in one word."}]
        response = await llm._call_llm(messages, model_name, max_tokens=10)
        
        if response and 'choices' in response:
            content = response['choices'][0]['message']['content']
            print(f"   ✅ SUCCESS: {content[:50]}")
            return True
        else:
            print(f"   ❌ FAILED: Unexpected response format")
            return False
            
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)[:100]}")
        return False

async def main():
    print("=" * 60)
    print("🔍 Model Call Debugging")
    print("=" * 60)
    
    # Test models that are configured
    test_models = [
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "groq/compound",
        "openai/gpt-oss-20b",
    ]
    
    results = {}
    for model in test_models:
        results[model] = await test_model_call(model)
    
    print("\n" + "=" * 60)
    print("📊 Results Summary")
    print("=" * 60)
    for model, success in results.items():
        status = "✅ WORKING" if success else "❌ FAILED"
        print(f"{model}: {status}")

if __name__ == "__main__":
    asyncio.run(main())
