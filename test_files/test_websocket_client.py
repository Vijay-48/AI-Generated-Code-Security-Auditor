#!/usr/bin/env python3
"""
WebSocket Test Client for AI Code Security Auditor
Tests real-time progress updates during security scans
"""
import asyncio
import json
import aiohttp
import websockets
from datetime import datetime


async def test_websocket_client():
    """Test WebSocket real-time progress updates"""
    
    # First, submit a job
    print("🚀 Submitting security audit job...")
    
    async with aiohttp.ClientSession() as session:
        audit_data = {
            "code": "import os\nos.system('rm -rf /')\npassword = 'test123'\napi_key = 'sk-1234567890'",
            "language": "python",
            "use_advanced_analysis": False,
            "cache_enabled": False  # Disable cache to see full progress
        }
        
        async with session.post("http://localhost:8001/async/audit", 
                               json=audit_data) as response:
            job_data = await response.json()
            job_id = job_data["job_id"]
            print(f"📋 Job submitted: {job_id}")
    
    # Connect to WebSocket for progress updates
    websocket_url = f"ws://localhost:8001/async/jobs/{job_id}/ws"
    print(f"🔗 Connecting to WebSocket: {websocket_url}")
    
    try:
        async with websockets.connect(websocket_url) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Send initial ping
            await websocket.send(json.dumps({"type": "ping"}))
            print("📤 Sent ping to server")
            
            # Listen for updates
            progress_updates = []
            completed = False
            
            while not completed:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message_type = data.get("type", "unknown")
                    
                    if message_type == "connection":
                        print(f"[{timestamp}] 🔗 {data.get('message', 'Connected')}")
                    
                    elif message_type == "pong":
                        print(f"[{timestamp}] 🏓 Pong received")
                    
                    elif message_type == "initial_status":
                        status = data.get("status", "unknown")
                        print(f"[{timestamp}] 📊 Initial status: {status}")
                        
                        if status == "completed":
                            print(f"[{timestamp}] ✅ Job already completed!")
                            completed = True
                    
                    elif message_type == "progress":
                        stage = data.get("stage", "unknown")
                        progress = data.get("progress", 0)
                        message = data.get("message", "Processing...")
                        status = data.get("status", "processing")
                        
                        progress_updates.append(data)
                        
                        # Progress bar
                        bar_length = 30
                        filled_length = int(bar_length * progress / 100)
                        bar = '█' * filled_length + '-' * (bar_length - filled_length)
                        
                        print(f"[{timestamp}] 📈 [{bar}] {progress:3.0f}% | {stage} | {message}")
                        
                        # Check if job is completed
                        if status in ["completed", "failed", "cancelled"]:
                            if status == "completed":
                                vulns = data.get("vulnerabilities_found", 0)
                                patches = data.get("patches_generated", 0)
                                exec_time = data.get("execution_time", 0)
                                print(f"[{timestamp}] ✅ Job completed! {vulns} vulnerabilities, {patches} patches, {exec_time:.1f}s")
                            elif status == "failed":
                                error = data.get("error", "Unknown error")
                                print(f"[{timestamp}] ❌ Job failed: {error}")
                            else:
                                print(f"[{timestamp}] 🚫 Job cancelled")
                            
                            completed = True
                    
                    elif message_type == "heartbeat":
                        active_clients = data.get("active_clients", 0)
                        print(f"[{timestamp}] 💓 Heartbeat (clients: {active_clients})")
                    
                    elif message_type == "error":
                        error = data.get("error", "Unknown error")
                        print(f"[{timestamp}] ❌ WebSocket error: {error}")
                        break
                    
                    else:
                        print(f"[{timestamp}] ❓ Unknown message type: {message_type}")
                        print(f"                   Data: {data}")
                
                except asyncio.TimeoutError:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Timeout waiting for message")
                    # Send ping to keep connection alive
                    await websocket.send(json.dumps({"type": "ping"}))
                
                except websockets.exceptions.ConnectionClosed:
                    print("🔌 WebSocket connection closed")
                    break
            
            print(f"\n📊 Summary:")
            print(f"   Total progress updates: {len(progress_updates)}")
            
            if progress_updates:
                stages = [update.get("stage", "unknown") for update in progress_updates]
                unique_stages = list(dict.fromkeys(stages))  # Preserve order
                print(f"   Stages observed: {', '.join(unique_stages)}")
                
                first_update = progress_updates[0]
                last_update = progress_updates[-1]
                
                start_time = first_update.get("started_at") or first_update.get("updated_at")
                end_time = last_update.get("completed_at") or last_update.get("updated_at")
                
                print(f"   Started: {start_time}")
                print(f"   Completed: {end_time}")
                
                if last_update.get("cache_hit"):
                    print(f"   💾 Result was cached (super fast!)")
                else:
                    exec_time = last_update.get("execution_time")
                    if exec_time:
                        print(f"   ⏱️  Execution time: {exec_time:.1f} seconds")
    
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")


async def test_multiple_clients():
    """Test multiple clients connecting to the same job"""
    print("\n🔄 Testing multiple WebSocket clients...")
    
    # Submit a job
    async with aiohttp.ClientSession() as session:
        audit_data = {
            "code": "password = 'hardcoded'\nimport subprocess\nsubprocess.call(['rm', '-rf', '/'])",
            "language": "python",
            "cache_enabled": False
        }
        
        async with session.post("http://localhost:8001/async/audit", 
                               json=audit_data) as response:
            job_data = await response.json()
            job_id = job_data["job_id"]
            print(f"📋 Job ID for multi-client test: {job_id}")
    
    # Create multiple WebSocket clients
    async def client_connection(client_id: int):
        websocket_url = f"ws://localhost:8001/async/jobs/{job_id}/ws"
        try:
            async with websockets.connect(websocket_url) as websocket:
                print(f"🔗 Client {client_id} connected")
                
                message_count = 0
                while message_count < 10:  # Listen for 10 messages
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        data = json.loads(message)
                        message_count += 1
                        
                        if data.get("type") == "progress":
                            progress = data.get("progress", 0)
                            stage = data.get("stage", "unknown")
                            print(f"👤 Client {client_id}: {progress}% - {stage}")
                            
                            if data.get("status") in ["completed", "failed"]:
                                break
                    
                    except asyncio.TimeoutError:
                        print(f"👤 Client {client_id}: Timeout")
                        break
                
                print(f"🔌 Client {client_id} disconnecting")
                
        except Exception as e:
            print(f"❌ Client {client_id} error: {e}")
    
    # Run multiple clients concurrently
    await asyncio.gather(
        client_connection(1),
        client_connection(2),
        client_connection(3)
    )


async def test_websocket_stats():
    """Test WebSocket statistics endpoint"""
    print("\n📊 Testing WebSocket statistics...")
    
    async with aiohttp.ClientSession() as session:
        async with session.get("http://localhost:8001/async/websocket/stats") as response:
            if response.status == 200:
                stats = await response.json()
                print(f"✅ WebSocket stats retrieved:")
                print(f"   Total connections: {stats['websocket_stats']['total_connections']}")
                print(f"   Active jobs: {stats['websocket_stats']['active_jobs']}")
                print(f"   Redis status: {stats['redis_status']}")
                if stats['websocket_stats']['jobs_with_clients']:
                    print(f"   Jobs with clients: {stats['websocket_stats']['jobs_with_clients']}")
            else:
                print(f"❌ Failed to get stats: {response.status}")


async def main():
    """Run all WebSocket tests"""
    print("🧪 Starting WebSocket Tests for AI Code Security Auditor")
    print("=" * 60)
    
    try:
        # Test basic WebSocket functionality
        await test_websocket_client()
        
        # Test WebSocket statistics
        await test_websocket_stats()
        
        # Test multiple clients (optional)
        # await test_multiple_clients()
        
        print("\n🎉 All WebSocket tests completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())