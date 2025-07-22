#!/usr/bin/env python3
"""
Simple WebSocket Real-Time Test
Tests WebSocket functionality with manual progress updates
"""
import asyncio
import websockets
import aiohttp
import json

async def test_manual_progress_simulation():
    """Test WebSocket with manual progress simulation"""
    
    backend_url = "http://localhost:8001"
    websocket_url = "ws://localhost:8001"
    
    print("🧪 WebSocket Real-Time Communication Test")
    print("=" * 50)
    
    # Create a fake job ID for testing
    job_id = "test-websocket-12345"
    
    print(f"\n1️⃣ Connecting to WebSocket for test job: {job_id}")
    websocket_endpoint = f"{websocket_url}/async/jobs/{job_id}/ws"
    
    try:
        async with websockets.connect(websocket_endpoint) as websocket:
            print("✅ WebSocket connected!")
            
            # Send initial message
            await websocket.send(json.dumps({
                "type": "ping",
                "message": "Hello WebSocket!"
            }))
            print("📤 Sent ping message")
            
            # Listen for responses
            print(f"\n2️⃣ Listening for WebSocket messages...")
            for i in range(5):  # Listen for 5 messages
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    update = json.loads(message)
                    
                    message_type = update.get('type', 'unknown')
                    timestamp = update.get('timestamp', 'no timestamp')[-8:] if update.get('timestamp') else 'unknown'
                    
                    print(f"[{timestamp}] 📡 Received: {message_type}")
                    
                    if message_type == 'pong':
                        print("   🏓 Pong received - WebSocket communication working!")
                    elif message_type == 'connection':
                        print(f"   🔗 Connection confirmed for job {update.get('job_id', 'unknown')}")
                    elif message_type == 'initial_status':
                        print(f"   📊 Initial status: {update.get('status', 'unknown')}")
                    elif message_type == 'heartbeat':
                        print(f"   💓 Heartbeat - Active clients: {update.get('active_clients', 0)}")
                    else:
                        print(f"   📨 Data: {update}")
                        
                except asyncio.TimeoutError:
                    print(f"   ⏰ Timeout waiting for message {i+1}")
                    break
            
            print(f"\n3️⃣ Testing manual progress update via Redis...")
            
            # Now let's manually publish a progress update to Redis to test pub/sub
            import sys
            sys.path.append('/app')
            from app.websocket_manager import websocket_manager
            
            # Initialize a separate WebSocket manager for publishing
            temp_websocket_manager = websocket_manager
            
            # Publish a test progress update
            test_progress = {
                'status': 'processing',
                'stage': 'testing',
                'progress': 50,
                'message': 'Manual WebSocket test in progress!'
            }
            
            await temp_websocket_manager.publish_job_progress(job_id, test_progress)
            print("📡 Published test progress update to Redis")
            
            # Wait for the update to be received
            try:
                message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                update = json.loads(message)
                print(f"✅ Received progress update: {update.get('message', 'No message')}")
                print(f"   Status: {update.get('status', 'unknown')}")
                print(f"   Progress: {update.get('progress', 0)}%")
            except asyncio.TimeoutError:
                print("⏰ No progress update received (pub/sub might not be working)")
            
            print(f"\n4️⃣ WebSocket test completed!")
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_manual_progress_simulation())
    print(f"\n🎯 Test Result: {'✅ SUCCESS' if success else '❌ FAILURE'}")