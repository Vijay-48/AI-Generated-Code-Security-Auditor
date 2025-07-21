#!/usr/bin/env python3

import os
import sys
import asyncio
sys.path.append("/app")

from app.services.llm_client import query_openrouter, ModelType

async def test_openrouter():
    """Test OpenRouter integration with the API key"""
    try:
        # Set the API key directly
        os.environ["OPENROUTER_API_KEY"] = "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"
        
        print("Testing OpenRouter API connection...")
        
        # Test simple query
        response = query_openrouter(
            "Say 'Hello! OpenRouter is working!' in a single line.",
            model=ModelType.DEEPCODER,
            max_tokens=50
        )
        
        print("✅ OpenRouter API Response:")
        print(response[:200] + "..." if len(response) > 200 else response)
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter API Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openrouter())
    print("\n" + "="*50)
    if success:
        print("✅ OpenRouter Integration: WORKING")
        print("🚀 Ready to proceed with full testing!")
    else:
        print("❌ OpenRouter Integration: FAILED") 
        print("🔑 Check API key configuration")