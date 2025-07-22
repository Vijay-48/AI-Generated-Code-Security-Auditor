#!/usr/bin/env python3
"""
Simple WebSocket Test for Real-Time Progress Updates
"""
import asyncio
import aiohttp
import json
import websockets
from datetime import datetime

async def quick_websocket_test():
    """Quick test of WebSocket real-time updates"""
    
    backend_url = "http://localhost:8001"
    websocket_url = "ws://localhost:8001"
    
    print("🧪 Quick WebSocket Test - Real-Time Progress Updates")
    print("=" * 60)
    
    # Submit a simple job
    print("\n1️⃣ Submitting new audit job...")
    audit_payload = {
        "code": "import os\nos.system('rm -rf /')",
        "language": "python",
        "filename": "test.py",
        "cache_enabled": False,  # Disable cache for full process
        "use_advanced_analysis": False  # Keep it simple for now
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{backend_url}/async/audit", json=audit_payload) as resp:
            job_response = await resp.json()
            job_id = job_response["job_id"]
            print(f"✅ New job submitted: {job_id}")
    
    # Connect to WebSocket immediately
    print(f"\n2️⃣ Connecting to WebSocket...")
    websocket_endpoint = f"{websocket_url}/async/jobs/{job_id}/ws"
    
    try:
        async with websockets.connect(websocket_endpoint) as websocket:
            print("✅ WebSocket connected!")
            
            print(f"\n3️⃣ Monitoring progress for job {job_id}:")
            print("-" * 50)
            
            timeout_count = 0
            max_timeout = 10  # 10 timeouts = ~5 minutes max
            
            while timeout_count < max_timeout:
                try:
                    # Wait for progress update
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    update = json.loads(message)
                    
                    # Display update
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message_type = update.get('type', 'unknown')
                    status = update.get('status', 'unknown')
                    stage = update.get('stage', '')
                    progress = update.get('progress', 0)
                    message_text = update.get('message', '')
                    
                    print(f"[{timestamp}] 📡 {message_type}: {status}", end="")
                    if stage:
                        print(f" | Stage: {stage}", end="")
                    if progress > 0:
                        print(f" | Progress: {progress}%", end="")
                    print()
                    
                    if message_text:
                        print(f"          💬 {message_text}")
                    
                    # Check for completion
                    if status in ['completed', 'failed']:
                        print(f"\n🎉 Job {status}!")
                        if 'execution_time' in update:
                            print(f"⏱️ Execution time: {update['execution_time']:.1f}s")
                        if 'vulnerabilities_found' in update:
                            print(f"🔍 Vulnerabilities found: {update['vulnerabilities_found']}")
                        break
                    
                    print()  # Empty line for readability
                    
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Timeout {timeout_count}/{max_timeout}")
                    if timeout_count >= max_timeout:
                        print("❌ Max timeouts reached")
                        break
            
            print(f"\n4️⃣ WebSocket test completed for job {job_id}")
    
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(quick_websocket_test())