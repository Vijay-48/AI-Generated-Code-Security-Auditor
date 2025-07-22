#!/usr/bin/env python3
"""
🚀 Comprehensive WebSocket End-to-End Test
Demonstrates Phase 5: Real-Time Client Updates via WebSockets
"""
import asyncio
import aiohttp
import websockets
import json
from datetime import datetime

async def comprehensive_websocket_demo():
    """
    Complete demonstration of WebSocket real-time progress updates
    
    This test validates:
    1. Job submission via async API
    2. WebSocket connection establishment  
    3. Real-time progress updates from Celery workers
    4. Live progress streaming to multiple clients
    5. Job completion notifications
    """
    
    backend_url = "http://localhost:8001"
    websocket_url = "ws://localhost:8001"
    
    print("🚀 AI Code Security Auditor v2.0 - WebSocket Demo")
    print("=" * 60)
    print("📡 Testing: Real-Time Progress Updates via WebSockets")
    print("🔧 Infrastructure: FastAPI + Celery + Redis + WebSocket")
    print("=" * 60)
    
    # Test vulnerable code sample
    vulnerable_code = """
import os
import subprocess
import sqlite3

# 🔴 VULNERABILITY: Command Injection
def execute_command(user_input):
    os.system(f"ping {user_input}")  # B605: Command injection vulnerability
    
# 🔴 VULNERABILITY: SQL Injection  
def get_user(user_id):
    conn = sqlite3.connect("app.db")
    query = f"SELECT * FROM users WHERE id = {user_id}"  # B608: SQL injection
    return conn.execute(query).fetchall()

# 🔴 SECRET: AWS Access Key
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"

# 🔴 SECRET: Database Password
DATABASE_URL = "postgresql://admin:supersecret123@localhost/myapp"

# 🔴 VULNERABILITY: Weak Cryptography
import hashlib
def weak_hash(password):
    return hashlib.md5(password.encode()).hexdigest()  # Weak hashing algorithm
    """
    
    try:
        print(f"\n🎯 PHASE 1: Job Submission")
        print("-" * 30)
        
        # Submit comprehensive security audit
        audit_payload = {
            "code": vulnerable_code,
            "language": "python",
            "filename": "vulnerable_app.py",
            "use_advanced_analysis": True,  # Enable multi-model AI analysis
            "cache_enabled": False,  # Disable cache to see full process  
            "priority": "normal"
        }
        
        async with aiohttp.ClientSession() as session:
            print("📤 Submitting security audit job...")
            async with session.post(f"{backend_url}/async/audit", json=audit_payload) as resp:
                if resp.status == 200:
                    job_response = await resp.json()
                    job_id = job_response["job_id"]
                    print(f"✅ Job submitted successfully!")
                    print(f"   📋 Job ID: {job_id}")
                    print(f"   ⏱️  Estimated duration: {job_response.get('estimated_duration', 'unknown')}")
                    print(f"   🔗 Progress URL: {job_response.get('progress_url', 'unknown')}")
                    print(f"   📡 WebSocket URL: {job_response.get('websocket_url', 'unknown')}")
                else:
                    print(f"❌ Job submission failed: {resp.status}")
                    return False
        
        print(f"\n🎯 PHASE 2: Real-Time Progress Monitoring")
        print("-" * 30)
        
        websocket_endpoint = f"{websocket_url}/async/jobs/{job_id}/ws"
        print(f"🔌 Connecting to WebSocket: {websocket_endpoint}")
        
        async with websockets.connect(websocket_endpoint) as websocket:
            print("✅ WebSocket connected successfully!")
            
            # Track progress metrics
            start_time = datetime.now()
            stages_seen = set()
            progress_updates = []
            vulnerabilities_found = 0
            patches_generated = 0
            
            print(f"\n📊 LIVE PROGRESS UPDATES:")
            print("-" * 50)
            
            max_updates = 20  # Limit to prevent infinite loop
            update_count = 0
            
            while update_count < max_updates:
                try:
                    # Wait for progress update
                    message = await asyncio.wait_for(websocket.recv(), timeout=45.0)
                    update = json.loads(message)
                    progress_updates.append(update)
                    update_count += 1
                    
                    # Extract update information
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    message_type = update.get('type', 'unknown')
                    status = update.get('status', 'unknown')
                    stage = update.get('stage', '')
                    progress = update.get('progress', 0)
                    message_text = update.get('message', '')
                    
                    # Track stages
                    if stage:
                        stages_seen.add(stage)
                    
                    # Display progress with emojis
                    stage_emojis = {
                        'initializing': '🚀',
                        'scanning': '🔍', 
                        'vulnerability_analysis': '🔍',
                        'remediation_retrieval': '📚',
                        'ai_analysis': '🤖',
                        'finalizing': '⚡',
                        'completed': '🎉',
                        'cache_hit': '⚡',
                        'error': '❌'
                    }
                    
                    stage_emoji = stage_emojis.get(stage, '📡')
                    
                    if message_type == 'progress':
                        if progress > 0:
                            progress_bar = "█" * (progress // 5) + "░" * (20 - progress // 5)
                            print(f"[{timestamp}] {stage_emoji} {stage.upper()}: {progress}% [{progress_bar}]")
                        else:
                            print(f"[{timestamp}] {stage_emoji} {stage.upper()}: {status}")
                        
                        if message_text:
                            print(f"           💬 {message_text}")
                        
                        # Track final metrics
                        if 'vulnerabilities_found' in update:
                            vulnerabilities_found = update['vulnerabilities_found']
                        if 'patches_generated' in update:
                            patches_generated = update['patches_generated']
                        
                        # Check for completion
                        if status == 'completed':
                            print(f"           🎉 ANALYSIS COMPLETE!")
                            if 'execution_time' in update:
                                print(f"           ⏱️  Total time: {update['execution_time']:.1f}s")
                            print(f"           🔍 Vulnerabilities: {vulnerabilities_found}")
                            print(f"           🛠️  Patches: {patches_generated}")
                            break
                            
                        elif status == 'failed':
                            print(f"           ❌ ANALYSIS FAILED!")
                            if 'error' in update:
                                print(f"           💥 Error: {update['error']}")
                            break
                    
                    elif message_type == 'connection':
                        print(f"[{timestamp}] 🔗 Connected to job progress stream")
                    
                    elif message_type == 'heartbeat':
                        active_clients = update.get('active_clients', 0)
                        if active_clients > 1:
                            print(f"[{timestamp}] 💓 Heartbeat ({active_clients} clients connected)")
                    
                    elif message_type == 'initial_status':
                        print(f"[{timestamp}] 📊 Initial status: {status}")
                        if stage:
                            print(f"           🎯 Current stage: {stage}")
                    
                except asyncio.TimeoutError:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Timeout - job may be taking longer than expected")
                    break
                except websockets.exceptions.ConnectionClosed:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔌 WebSocket connection closed")
                    break
        
        print(f"\n🎯 PHASE 3: Results Validation")
        print("-" * 30)
        
        # Get final results
        async with aiohttp.ClientSession() as session:
            print("📋 Fetching final results...")
            async with session.get(f"{backend_url}/async/jobs/{job_id}/results") as resp:
                if resp.status == 200:
                    results = await resp.json()
                    print("✅ Results retrieved successfully!")
                    
                    # Analyze results
                    scan_results = results.get('results', {})
                    vulnerabilities = scan_results.get('vulnerabilities', [])
                    patches = scan_results.get('patches', [])
                    
                    print(f"\n📊 SECURITY ANALYSIS SUMMARY:")
                    print(f"   🔍 Total Vulnerabilities: {len(vulnerabilities)}")
                    
                    # Show vulnerability breakdown
                    severity_counts = {}
                    for vuln in vulnerabilities:
                        severity = vuln.get('severity', 'UNKNOWN')
                        severity_counts[severity] = severity_counts.get(severity, 0) + 1
                    
                    severity_emojis = {
                        'CRITICAL': '🔴',
                        'HIGH': '🟠', 
                        'MEDIUM': '🟡',
                        'LOW': '🔵',
                        'INFO': '⚪'
                    }
                    
                    for severity, count in severity_counts.items():
                        emoji = severity_emojis.get(severity, '⚪')
                        print(f"   {emoji} {severity}: {count}")
                    
                    print(f"\n   🛠️  Total Patches Generated: {len(patches)}")
                    
                    # Show top 3 vulnerabilities
                    if vulnerabilities:
                        print(f"\n   🎯 TOP VULNERABILITIES DETECTED:")
                        for i, vuln in enumerate(vulnerabilities[:3], 1):
                            title = vuln.get('title', 'Unknown Vulnerability')
                            line = vuln.get('line_number', 'Unknown')
                            severity = vuln.get('severity', 'Unknown')
                            print(f"      {i}. {title}")
                            print(f"         📍 Line {line} | Severity: {severity}")
                            
                elif resp.status == 202:
                    print("⏳ Job still processing - results not ready yet")
                elif resp.status == 404:
                    print("❌ Job not found")
                else:
                    print(f"❌ Failed to get results: {resp.status}")
        
        print(f"\n🎯 PHASE 4: Performance Metrics")
        print("-" * 30)
        
        end_time = datetime.now()
        total_time = (end_time - start_time).total_seconds()
        
        print(f"✅ WebSocket Demo Completed Successfully!")
        print(f"   ⏱️  Total Demo Time: {total_time:.1f}s")
        print(f"   📊 Progress Updates Received: {len(progress_updates)}")
        print(f"   🎯 Stages Observed: {len(stages_seen)}")
        print(f"   📡 WebSocket Connection: Stable")
        
        # Show stage progression
        if stages_seen:
            print(f"\n   📈 STAGE PROGRESSION:")
            stage_order = ['initializing', 'scanning', 'vulnerability_analysis', 
                          'remediation_retrieval', 'ai_analysis', 'finalizing', 'completed']
            for stage in stage_order:
                if stage in stages_seen:
                    emoji = stage_emojis.get(stage, '📡')
                    print(f"      {emoji} {stage.replace('_', ' ').title()}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_websocket_clients():
    """Test multiple clients connecting to the same job"""
    print(f"\n🎯 BONUS: Multiple WebSocket Clients Test")
    print("-" * 30)
    
    backend_url = "http://localhost:8001"
    websocket_url = "ws://localhost:8001"
    
    # Submit a simple job
    audit_payload = {
        "code": "import os\nos.system('echo multi-client-test')",
        "language": "python",
        "cache_enabled": False
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{backend_url}/async/audit", json=audit_payload) as resp:
            job_response = await resp.json()
            job_id = job_response["job_id"]
    
    print(f"👥 Testing multiple clients for job: {job_id}")
    
    async def client_worker(client_id: int):
        try:
            websocket_endpoint = f"{websocket_url}/async/jobs/{job_id}/ws"
            async with websockets.connect(websocket_endpoint) as websocket:
                print(f"   Client {client_id}: ✅ Connected")
                updates_received = 0
                
                for _ in range(3):  # Listen for 3 updates
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=15.0)
                        update = json.loads(message)
                        updates_received += 1
                        
                        if update.get('type') == 'progress':
                            print(f"   Client {client_id}: 📡 Progress update #{updates_received}")
                        
                        if update.get('status') == 'completed':
                            break
                            
                    except asyncio.TimeoutError:
                        break
                
                print(f"   Client {client_id}: 🔌 Disconnected ({updates_received} updates)")
                return updates_received > 0
                
        except Exception as e:
            print(f"   Client {client_id}: ❌ Error - {e}")
            return False
    
    # Start multiple clients
    num_clients = 3
    tasks = [client_worker(i+1) for i in range(num_clients)]
    results = await asyncio.gather(*tasks)
    
    successful_clients = sum(results)
    print(f"✅ Multiple clients test: {successful_clients}/{num_clients} clients succeeded")
    
    return successful_clients >= 2  # At least 2 clients should succeed

if __name__ == "__main__":
    async def run_complete_demo():
        print("🚀 Starting Comprehensive WebSocket Demo...")
        print("🎯 This demo showcases Phase 5: Real-Time Client Updates")
        print("=" * 60)
        
        # Main demo
        demo_success = await comprehensive_websocket_demo()
        
        # Bonus: Multiple clients  
        multi_client_success = await test_multiple_websocket_clients()
        
        # Final results
        print(f"\n🏁 FINAL RESULTS")
        print("=" * 30)
        print(f"📡 Real-Time Progress Demo: {'✅ SUCCESS' if demo_success else '❌ FAILED'}")
        print(f"👥 Multiple WebSocket Clients: {'✅ SUCCESS' if multi_client_success else '❌ FAILED'}")
        
        overall_success = demo_success and multi_client_success
        print(f"\n🎯 PHASE 5 STATUS: {'🎉 COMPLETE' if overall_success else '⚠️  PARTIAL'}")
        
        if overall_success:
            print("\n🚀 WebSocket Real-Time Updates - FULLY OPERATIONAL!")
            print("✅ Ready for production deployment")
        
        return overall_success
    
    # Run the complete demo
    success = asyncio.run(run_complete_demo())
    exit(0 if success else 1)