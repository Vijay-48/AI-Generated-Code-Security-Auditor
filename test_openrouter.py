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