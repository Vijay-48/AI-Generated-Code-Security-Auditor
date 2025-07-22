"""
Analytics API Endpoints for Phase 7: Advanced Monitoring Dashboards
Provides REST API and WebSocket endpoints for dashboard data
"""
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Query
from pydantic import BaseModel

from app.models.analytics import (
    DashboardOverview, SecurityMetrics, VulnerabilityTrend, RepositoryStats,
    VulnerabilityDistribution, ScanPerformanceMetrics, TimeRange, SeverityLevel,
    ExportRequest, ExportResponse, AlertConfig, ScanRecord, RuleHitRecord, ExportFormat
)
from app.services.analytics_service import analytics_service
from app.websocket_manager import websocket_manager

# Create router for analytics endpoints
analytics_router = APIRouter(prefix="/api/analytics", tags=["Analytics & Dashboards"])

class RealtimeAnalyticsManager:
    """Manages real-time analytics WebSocket connections"""
    
    def __init__(self):
        self.active_connections = {}
        self.update_task = None
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept analytics WebSocket connection"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        
        # Start real-time updates if not already running
        if not self.update_task or self.update_task.done():
            self.update_task = asyncio.create_task(self._send_periodic_updates())
        
        print(f"📊 Analytics client connected: {client_id}")
        
        # Send initial dashboard data
        try:
            overview = await analytics_service.get_dashboard_overview(TimeRange.LAST_DAY)
            await websocket.send_json({
                "type": "dashboard_update",
                "data": overview.model_dump(),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            print(f"⚠️ Error sending initial dashboard data: {e}")
    
    def disconnect(self, client_id: str):
        """Remove WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"📊 Analytics client disconnected: {client_id}")
    
    async def broadcast_update(self, update_data: Dict[str, Any]):
        """Broadcast analytics update to all connected clients"""
        if not self.active_connections:
            return
            
        message = {
            "type": "live_update",
            "data": update_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        disconnected_clients = []
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                print(f"⚠️ Failed to send update to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def _send_periodic_updates(self):
        """Send periodic dashboard updates every 30 seconds"""
        while self.active_connections:
            try:
                await asyncio.sleep(30)
                
                if not self.active_connections:
                    break
                
                # Get fresh metrics
                metrics = await analytics_service.get_security_metrics(TimeRange.LAST_HOUR)
                
                await self.broadcast_update({
                    "metrics": metrics.model_dump(),
                    "update_type": "periodic"
                })
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️ Error in periodic analytics updates: {e}")
                await asyncio.sleep(10)  # Wait before retry

# Global analytics manager
analytics_manager = RealtimeAnalyticsManager()

# API Endpoints

@analytics_router.get("/overview", response_model=DashboardOverview)
async def get_dashboard_overview(
    time_range: TimeRange = Query(TimeRange.LAST_DAY, description="Time range for dashboard data")
):
    """
    **📊 Dashboard Overview - Complete analytics snapshot**
    
    Returns comprehensive dashboard data including:
    - Security metrics and scores
    - Vulnerability trends over time
    - Top repositories by security score
    - Performance metrics
    - Time series data
    
    **Time Ranges:**
    - `1h` - Last hour
    - `24h` - Last 24 hours (default)  
    - `7d` - Last 7 days
    - `30d` - Last 30 days
    - `90d` - Last quarter
    - `365d` - Last year
    """
    try:
        overview = await analytics_service.get_dashboard_overview(time_range)
        return overview
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard overview: {str(e)}")

@analytics_router.get("/metrics", response_model=SecurityMetrics)
async def get_security_metrics(
    time_range: TimeRange = Query(TimeRange.LAST_DAY, description="Time range for metrics")
):
    """
    **🔐 Security Metrics - Key performance indicators**
    
    Returns aggregated security metrics:
    - Total scans, files, and repositories
    - Vulnerability counts by severity
    - Security score (0-100)
    - Performance indicators
    - Recent activity summary
    """
    try:
        metrics = await analytics_service.get_security_metrics(time_range)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get security metrics: {str(e)}")

@analytics_router.get("/trends", response_model=List[VulnerabilityTrend])
async def get_vulnerability_trends(
    time_range: TimeRange = Query(TimeRange.LAST_WEEK, description="Time range for trends"),
    severity: Optional[SeverityLevel] = Query(None, description="Filter by severity level"),
    repository: Optional[str] = Query(None, description="Filter by repository URL")
):
    """
    **📈 Vulnerability Trends - Historical analysis**
    
    Returns vulnerability trends over time:
    - Time-series vulnerability data
    - Severity breakdowns
    - Repository-specific trends
    - Scan type analysis
    """
    try:
        trends = await analytics_service.get_vulnerability_trends(time_range)
        
        # Apply filters
        if severity:
            trends = [t for t in trends if t.severity == severity]
        
        if repository:
            trends = [t for t in trends if t.repository and repository in t.repository]
        
        return trends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get vulnerability trends: {str(e)}")

@analytics_router.get("/repositories", response_model=List[RepositoryStats])
async def get_repository_statistics(
    limit: int = Query(20, description="Maximum number of repositories to return"),
    min_score: Optional[float] = Query(None, description="Minimum security score filter"),
    sort_by: str = Query("security_score", description="Sort field (security_score, vulnerabilities, scans)")
):
    """
    **📁 Repository Statistics - Per-repository insights**
    
    Returns detailed statistics for repositories:
    - Security scores and rankings
    - Vulnerability counts and distributions
    - Scan history and performance
    - File statistics
    - Language breakdown
    """
    try:
        repos = await analytics_service.get_repository_stats(limit * 2)  # Get extra for filtering
        
        # Apply filters
        if min_score is not None:
            repos = [r for r in repos if r.security_score >= min_score]
        
        # Apply sorting
        if sort_by == "vulnerabilities":
            repos.sort(key=lambda x: x.total_vulnerabilities, reverse=True)
        elif sort_by == "scans":
            repos.sort(key=lambda x: x.total_scans, reverse=True)
        # Default is already sorted by security_score
        
        return repos[:limit]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get repository statistics: {str(e)}")

@analytics_router.get("/performance", response_model=List[ScanPerformanceMetrics])
async def get_performance_metrics():
    """
    **⚡ Performance Metrics - System performance analysis**
    
    Returns scan performance metrics:
    - Average, min, max scan times
    - Success and failure rates
    - Cache hit rates
    - Resource utilization
    - Performance by scan type
    """
    try:
        performance = await analytics_service.get_performance_metrics()
        return performance
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {str(e)}")

@analytics_router.get("/health")
async def analytics_health_check():
    """Analytics service health check"""
    try:
        # Test analytics service connection
        if not analytics_service.redis_client:
            await analytics_service.connect()
        
        # Quick metrics test
        metrics = await analytics_service.get_security_metrics(TimeRange.LAST_HOUR)
        
        return {
            "status": "healthy",
            "analytics_service": "connected",
            "sample_metrics": {
                "total_scans": metrics.total_scans,
                "cache_hit_rate": metrics.cache_hit_rate
            },
            "active_dashboard_clients": len(analytics_manager.active_connections)
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Analytics service unhealthy: {str(e)}")

# Real-time WebSocket endpoint
@analytics_router.websocket("/ws")
async def analytics_websocket(websocket: WebSocket):
    """
    **⚡ Real-time Analytics WebSocket**
    
    Provides live dashboard updates:
    - Real-time metrics updates every 30 seconds
    - Immediate notifications for new scans
    - Live vulnerability trend data
    - Performance metrics streaming
    
    **Connection Protocol:**
    1. Connect to `/api/analytics/ws`
    2. Receive initial dashboard data
    3. Get periodic updates every 30 seconds
    4. Receive immediate updates for new scan results
    
    **Message Types:**
    - `dashboard_update` - Complete dashboard refresh
    - `live_update` - Incremental metrics update
    - `scan_completed` - New scan result notification
    """
    
    client_id = f"analytics_{id(websocket)}"
    
    try:
        await analytics_manager.connect(websocket, client_id)
        
        while True:
            try:
                # Wait for client messages (ping, requests, etc.)
                data = await asyncio.wait_for(websocket.receive_json(), timeout=60.0)
                
                # Handle client requests
                if data.get("type") == "request_update":
                    time_range = TimeRange(data.get("time_range", "24h"))
                    overview = await analytics_service.get_dashboard_overview(time_range)
                    
                    await websocket.send_json({
                        "type": "dashboard_update",
                        "data": overview.model_dump(),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                elif data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                    
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "active_clients": len(analytics_manager.active_connections),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                
    except WebSocketDisconnect:
        analytics_manager.disconnect(client_id)
    except Exception as e:
        print(f"⚠️ Analytics WebSocket error: {e}")
        analytics_manager.disconnect(client_id)

# Export endpoints (for future implementation)
@analytics_router.post("/export", response_model=ExportResponse)
async def export_dashboard_data(request: ExportRequest):
    """
    **📊 Export Dashboard Data - Generate reports**
    
    Export dashboard data in various formats:
    - CSV - Comma-separated values for analysis
    - PDF - Formatted report document
    - JSON - Raw data for API integration
    - XLSX - Excel spreadsheet format
    
    **Note:** This endpoint is prepared for Phase 7 enhancement.
    Currently returns a placeholder response.
    """
    # Placeholder implementation
    return ExportResponse(
        export_id=f"export_{int(datetime.now().timestamp())}",
        status="not_implemented",
        download_url=None
    )

# Integration with existing scan completion
async def notify_scan_completed(job_id: str, scan_results: Dict[str, Any]):
    """
    Called when a scan completes to update real-time dashboards
    This function should be called from the scan workers
    """
    try:
        # Extract relevant metrics from scan results
        update_data = {
            "job_id": job_id,
            "update_type": "scan_completed",
            "vulnerabilities_found": len(scan_results.get("vulnerabilities", [])),
            "scan_duration": scan_results.get("metadata", {}).get("execution_time"),
            "repository": scan_results.get("metadata", {}).get("repository_url")
        }
        
        # Broadcast to analytics dashboard clients
        await analytics_manager.broadcast_update(update_data)
        
        # Also notify job-specific WebSocket clients through existing manager
        await websocket_manager.broadcast_to_job(job_id, "analytics_update", update_data)
        
    except Exception as e:
        print(f"⚠️ Error notifying scan completion to analytics: {e}")

# Startup function to initialize analytics service
async def initialize_analytics_service():
    """Initialize analytics service on application startup"""
    try:
        await analytics_service.connect()
        print("✅ Analytics service initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize analytics service: {e}")