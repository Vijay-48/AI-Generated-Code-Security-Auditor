"""
WebSocket Manager for Real-Time Progress Updates
Handles client connections and progress broadcasting from Celery workers
"""
import json
import asyncio
from typing import Dict, List, Set
from datetime import datetime, timezone

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis
from app.config import settings


class WebSocketConnectionManager:
    """
    Manages WebSocket connections and handles real-time progress broadcasting
    
    Features:
    - Multiple clients per job ID
    - Automatic cleanup of disconnected clients
    - Redis pub/sub for worker-to-client communication
    - Connection heartbeat and health monitoring
    """
    
    def __init__(self):
        # Active connections: job_id -> list of websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict] = {}
        
        # Redis client for pub/sub
        self.redis_pubsub = None
        self.redis_publisher = None
        
        # Background task for listening to Redis pub/sub
        self.pubsub_task = None
        
    async def initialize(self):
        """Initialize Redis pub/sub connections"""
        try:
            # Create Redis clients
            redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
            
            self.redis_publisher = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            
            # Create pub/sub client
            pubsub_redis = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            self.redis_pubsub = pubsub_redis.pubsub()
            
            # Subscribe to job progress channels
            await self.redis_pubsub.subscribe("job_progress:*")
            
            # Start background task to listen for updates
            self.pubsub_task = asyncio.create_task(self._listen_for_updates())
            
            print("✅ WebSocket manager initialized with Redis pub/sub")
            
        except Exception as e:
            print(f"❌ Failed to initialize WebSocket manager: {e}")
    
    async def shutdown(self):
        """Cleanup Redis connections and background tasks"""
        if self.pubsub_task:
            self.pubsub_task.cancel()
        
        if self.redis_pubsub:
            await self.redis_pubsub.close()
        
        if self.redis_publisher:
            await self.redis_publisher.close()
    
    async def connect(self, websocket: WebSocket, job_id: str, client_info: Dict = None):
        """Accept WebSocket connection and register client"""
        await websocket.accept()
        
        if job_id not in self.active_connections:
            self.active_connections[job_id] = []
        
        self.active_connections[job_id].append(websocket)
        
        # Store connection metadata
        connection_id = f"{job_id}:{id(websocket)}"
        self.connection_metadata[connection_id] = {
            "job_id": job_id,
            "connected_at": datetime.now(timezone.utc).isoformat(),
            "client_info": client_info or {},
            "last_ping": datetime.now(timezone.utc).isoformat()
        }
        
        print(f"🔗 WebSocket connected for job {job_id} (total: {len(self.active_connections[job_id])})")
        
        # Send initial connection confirmation
        await websocket.send_json({
            "type": "connection",
            "job_id": job_id,
            "status": "connected",
            "message": f"Connected to job {job_id} progress stream",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    def disconnect(self, websocket: WebSocket, job_id: str):
        """Remove WebSocket connection"""
        if job_id in self.active_connections:
            try:
                self.active_connections[job_id].remove(websocket)
                
                # Clean up empty job lists
                if not self.active_connections[job_id]:
                    del self.active_connections[job_id]
                
                # Clean up metadata
                connection_id = f"{job_id}:{id(websocket)}"
                if connection_id in self.connection_metadata:
                    del self.connection_metadata[connection_id]
                
                print(f"🔌 WebSocket disconnected for job {job_id}")
                
            except ValueError:
                # Connection already removed
                pass
    
    async def send_progress_update(self, job_id: str, progress_data: Dict):
        """Send progress update to all clients subscribed to a job"""
        if job_id not in self.active_connections:
            return
        
        disconnected_clients = []
        message = {
            "type": "progress",
            "job_id": job_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **progress_data
        }
        
        for websocket in self.active_connections[job_id]:
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"⚠️ Failed to send to client: {e}")
                disconnected_clients.append(websocket)
        
        # Clean up disconnected clients
        for websocket in disconnected_clients:
            self.disconnect(websocket, job_id)
    
    async def publish_job_progress(self, job_id: str, progress_data: Dict):
        """Publish job progress to Redis for distribution to WebSocket clients"""
        if not self.redis_publisher:
            return
            
        try:
            channel = f"job_progress:{job_id}"
            message = json.dumps({
                "job_id": job_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **progress_data
            })
            
            await self.redis_publisher.publish(channel, message)
            
        except Exception as e:
            print(f"⚠️ Failed to publish job progress: {e}")
    
    async def _listen_for_updates(self):
        """Background task to listen for Redis pub/sub messages and broadcast to clients"""
        try:
            async for message in self.redis_pubsub.listen():
                if message["type"] == "message":
                    try:
                        # Parse message
                        channel = message["channel"]
                        data = json.loads(message["data"])
                        
                        # Extract job ID from channel name (job_progress:job_id)
                        if channel.startswith("job_progress:"):
                            job_id = channel.replace("job_progress:", "")
                            
                            # Broadcast to connected clients
                            await self.send_progress_update(job_id, data)
                        
                    except Exception as e:
                        print(f"⚠️ Error processing pub/sub message: {e}")
        
        except asyncio.CancelledError:
            print("📡 WebSocket pub/sub listener cancelled")
        except Exception as e:
            print(f"❌ WebSocket pub/sub listener error: {e}")
    
    async def broadcast_to_job(self, job_id: str, message_type: str, data: Dict):
        """Broadcast custom message to all clients of a specific job"""
        message = {
            "type": message_type,
            "job_id": job_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data
        }
        
        await self.send_progress_update(job_id, message)
    
    async def send_heartbeat(self, job_id: str):
        """Send heartbeat to keep connections alive"""
        await self.broadcast_to_job(job_id, "heartbeat", {
            "message": "Connection alive",
            "active_clients": len(self.active_connections.get(job_id, []))
        })
    
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        total_connections = sum(len(clients) for clients in self.active_connections.values())
        
        return {
            "total_connections": total_connections,
            "active_jobs": len(self.active_connections),
            "jobs_with_clients": list(self.active_connections.keys()),
            "connections_per_job": {
                job_id: len(clients) 
                for job_id, clients in self.active_connections.items()
            }
        }


# Global WebSocket manager instance
websocket_manager = WebSocketConnectionManager()