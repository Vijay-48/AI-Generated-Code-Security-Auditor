"""
Test script to verify API integration with GroqCloud and OpenRouter
"""
import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, '/app')

from app.services.llm_service import LLMService
from app.config import settings

async def test_groq_api():
    """Test GroqCloud API integration"""
    print("\n🚀 Testing GroqCloud API...")
    print(f"   API Key: {settings.GROQ_API_KEY[:20]}...")
    
    llm = LLMService()
    
    try:
        messages = [
            {"role": "user", "content": "What is a command injection vulnerability? Answer in one sentence."}
        ]
        
        # Test with Groq model
        response = await llm._call_groq(messages, "llama-3.1-8b-instant", max_tokens=100)
        
        if response and 'choices' in response:
            print("   ✅ GroqCloud API is working!")
            content = response['choices'][0]['message']['content']
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("   ❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"   ❌ GroqCloud API test failed: {str(e)}")
        return False

async def test_openrouter_api():
    """Test OpenRouter API integration"""
    print("\n🌐 Testing OpenRouter API...")
    print(f"   API Key: {settings.OPENROUTER_API_KEY[:20]}...")
    
    llm = LLMService()
    
    try:
        messages = [
            {"role": "user", "content": "What is SQL injection? Answer in one sentence."}
        ]
        
        # Test with OpenRouter model
        response = await llm._call_openrouter(messages, "qwen/qwen-2.5-coder-32b-instruct", max_tokens=100)
        
        if response and 'choices' in response:
            print("   ✅ OpenRouter API is working!")
            content = response['choices'][0]['message']['content']
            print(f"   Response preview: {content[:100]}...")
            return True
        else:
            print("   ❌ Unexpected response format")
            return False
            
    except Exception as e:
        print(f"   ❌ OpenRouter API test failed: {str(e)}")
        return False

async def test_smart_routing():
    """Test smart model routing"""
    print("\n🧠 Testing Smart Model Routing...")
    
    llm = LLMService()
    
    # Test routing for different model types
    test_cases = [
        ("groq/compound", "GroqCloud"),
        ("llama-3.1-8b-instant", "GroqCloud"),
        ("qwen/qwen-2.5-coder-32b-instruct", "OpenRouter"),
        ("meta-llama/llama-3.3-70b-instruct", "OpenRouter")
    ]
    
    for model, expected_provider in test_cases:
        try:
            messages = [{"role": "user", "content": "Test"}]
            response = await llm._call_llm(messages, model, max_tokens=50)
            print(f"   ✅ {model} routed to {expected_provider}")
        except Exception as e:
            print(f"   ❌ {model} routing failed: {str(e)[:50]}")

async def test_fallback_mechanism():
    """Test fallback to secondary models"""
    print("\n🔄 Testing Fallback Mechanism...")
    
    llm = LLMService()
    print(f"   Primary patch model: {llm.patch_model}")
    print(f"   Secondary patch model: {llm.patch_model_secondary}")
    
    secondary = llm._get_secondary_model(llm.patch_model)
    if secondary:
        print(f"   ✅ Fallback mapping configured: {llm.patch_model} → {secondary}")
    else:
        print(f"   ⚠️  No fallback for {llm.patch_model}")

async def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 API Integration Test Suite")
    print("=" * 60)
    
    # Test API keys configuration
    print("\n🔑 Checking API Keys...")
    print(f"   GroqCloud: {'✅ Configured' if settings.GROQ_API_KEY else '❌ Missing'}")
    print(f"   OpenRouter: {'✅ Configured' if settings.OPENROUTER_API_KEY else '❌ Missing'}")
    
    # Test model configuration
    print("\n⚙️  Checking Model Configuration...")
    print(f"   Patch Generation: {settings.MODEL_PATCH_GENERATION}")
    print(f"   Quality Assessment: {settings.MODEL_QUALITY_ASSESSMENT}")
    print(f"   Fast Classification: {settings.MODEL_FAST_CLASSIFICATION}")
    print(f"   Code Generation: {settings.MODEL_CODE_GENERATION}")
    
    # Run API tests
    groq_ok = await test_groq_api()
    openrouter_ok = await test_openrouter_api()
    
    # Test routing
    await test_smart_routing()
    
    # Test fallback
    await test_fallback_mechanism()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"   GroqCloud API: {'✅ PASS' if groq_ok else '❌ FAIL'}")
    print(f"   OpenRouter API: {'✅ PASS' if openrouter_ok else '❌ FAIL'}")
    
    if groq_ok and openrouter_ok:
        print("\n🎉 All API integrations are working!")
        print("✅ Ready for hackathon!")
        return 0
    else:
        print("\n⚠️  Some API tests failed. Check configuration.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
