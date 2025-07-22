#!/usr/bin/env python3
"""
Test script to validate the complete WebSocket flow
"""
import asyncio
import aiohttp
import json

async def test_api_endpoints():
    """Test all the async API endpoints"""
    backend_url = "http://localhost:8001"
    
    print("🧪 Testing API Endpoints")
    print("=" * 40)
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        print("\n1️⃣ Testing health endpoint...")
        async with session.get(f"{backend_url}/health") as resp:
            if resp.status == 200:
                health = await resp.json()
                print(f"✅ Health: {health['status']}")
                print(f"   Version: {health['version']}")
                print(f"   Cache: {health.get('cache_status', 'unknown')}")
            else:
                print(f"❌ Health check failed: {resp.status}")
        
        # Test models endpoint
        print("\n2️⃣ Testing models endpoint...")
        async with session.get(f"{backend_url}/models") as resp:
            if resp.status == 200:
                models = await resp.json()
                print(f"✅ Available models: {len(models['available_models'])}")
            else:
                print(f"❌ Models endpoint failed: {resp.status}")
        
        # Test cache stats
        print("\n3️⃣ Testing cache stats...")
        async with session.get(f"{backend_url}/async/cache/stats") as resp:
            if resp.status == 200:
                stats = await resp.json()
                print(f"✅ Cache status: {stats.get('status', 'unknown')}")
                print(f"   Total keys: {stats.get('total_keys', 0)}")
            else:
                print(f"❌ Cache stats failed: {resp.status}")
        
        # Test websocket stats
        print("\n4️⃣ Testing WebSocket stats...")
        async with session.get(f"{backend_url}/async/websocket/stats") as resp:
            if resp.status == 200:
                ws_stats = await resp.json()
                print(f"✅ WebSocket connections: {ws_stats['websocket_stats']['total_connections']}")
                print(f"   Active jobs: {ws_stats['websocket_stats']['active_jobs']}")
                print(f"   Redis status: {ws_stats['redis_status']}")
            else:
                print(f"❌ WebSocket stats failed: {resp.status}")
        
        # Test sync audit (for comparison)
        print("\n5️⃣ Testing sync audit endpoint...")
        audit_payload = {
            "code": "import os\nos.system('echo test')",
            "language": "python"
        }
        
        async with session.post(f"{backend_url}/audit", json=audit_payload) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Sync audit completed")
                print(f"   Vulnerabilities: {len(result['vulnerabilities'])}")
                print(f"   Cache available: {result.get('cache_info', {}).get('cache_available', False)}")
            else:
                print(f"❌ Sync audit failed: {resp.status}")

if __name__ == "__main__":
    asyncio.run(test_api_endpoints())