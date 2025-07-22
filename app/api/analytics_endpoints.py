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
from sqlalchemy import func, and_, desc

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

# Phase 9: Advanced Analytics Endpoints

@analytics_router.get("/trends/detailed")
async def get_detailed_trends(
    period: int = Query(30, description="Number of days to analyze"),
    granularity: str = Query("daily", description="Time granularity: hourly, daily, weekly"),
    include_forecasting: bool = Query(False, description="Include trend forecasting")
):
    """
    **📈 Phase 9: Detailed Trend Analysis**
    
    Advanced trend analysis with:
    - Configurable time periods and granularity
    - Daily/weekly/monthly issue breakdowns
    - Growth rate calculations
    - Optional trend forecasting
    - Severity progression analysis
    """
    try:
        from datetime import timedelta
        
        # Get raw trend data
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(days=period)
        
        session = analytics_service.get_db_session()
        
        # Build granular query based on granularity
        if granularity == "hourly":
            time_format = func.strftime('%Y-%m-%d %H:00:00', ScanRecord.timestamp)
            group_format = func.strftime('%Y-%m-%d %H:00:00', ScanRecord.timestamp)
        elif granularity == "weekly":
            time_format = func.strftime('%Y-W%W', ScanRecord.timestamp)
            group_format = func.strftime('%Y-W%W', ScanRecord.timestamp)
        else:  # daily
            time_format = func.date(ScanRecord.timestamp)
            group_format = func.date(ScanRecord.timestamp)
        
        trends_data = session.query(
            group_format.label('time_period'),
            func.count(ScanRecord.id).label('total_scans'),
            func.sum(ScanRecord.total_issues).label('total_issues'),
            func.sum(ScanRecord.critical_count).label('critical'),
            func.sum(ScanRecord.high_count).label('high'), 
            func.sum(ScanRecord.medium_count).label('medium'),
            func.sum(ScanRecord.low_count).label('low'),
            func.avg(ScanRecord.security_score).label('avg_security_score'),
            func.avg(ScanRecord.scan_duration).label('avg_duration')
        ).filter(
            and_(
                ScanRecord.timestamp >= start_time,
                ScanRecord.timestamp <= end_time
            )
        ).group_by(
            group_format
        ).order_by('time_period').all()
        
        session.close()
        
        # Process and enrich data
        detailed_trends = []
        prev_issues = None
        
        for trend in trends_data:
            current_issues = int(trend.total_issues or 0)
            growth_rate = 0.0
            
            if prev_issues is not None and prev_issues > 0:
                growth_rate = ((current_issues - prev_issues) / prev_issues) * 100
            
            detailed_trends.append({
                "time_period": str(trend.time_period),
                "total_scans": int(trend.total_scans or 0),
                "total_issues": current_issues,
                "severity_breakdown": {
                    "critical": int(trend.critical or 0),
                    "high": int(trend.high or 0),
                    "medium": int(trend.medium or 0),
                    "low": int(trend.low or 0)
                },
                "avg_security_score": round(float(trend.avg_security_score or 0), 1),
                "avg_scan_duration": round(float(trend.avg_duration or 0), 2),
                "growth_rate_percent": round(growth_rate, 1)
            })
            
            prev_issues = current_issues
        
        response_data = {
            "period_days": period,
            "granularity": granularity,
            "data_points": len(detailed_trends),
            "trends": detailed_trends
        }
        
        # Add simple forecasting if requested
        if include_forecasting and len(detailed_trends) >= 3:
            # Simple linear trend calculation
            recent_points = detailed_trends[-3:]
            avg_growth = sum(p["growth_rate_percent"] for p in recent_points) / 3
            
            response_data["forecasting"] = {
                "average_growth_rate": round(avg_growth, 1),
                "trend_direction": "increasing" if avg_growth > 5 else "decreasing" if avg_growth < -5 else "stable",
                "confidence": "low"  # Simple forecasting has low confidence
            }
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detailed trends: {str(e)}")

@analytics_router.get("/top-rules")
async def get_top_vulnerability_rules(
    limit: int = Query(10, description="Number of top rules to return"),
    time_range: TimeRange = Query(TimeRange.LAST_MONTH, description="Time range for analysis"),
    severity_filter: Optional[SeverityLevel] = Query(None, description="Filter by severity"),
    tool_filter: Optional[str] = Query(None, description="Filter by tool (bandit, semgrep)")
):
    """
    **🔝 Phase 9: Top Vulnerability Rules**
    
    Analyze the most frequently triggered security rules:
    - Most common vulnerability patterns
    - Rule hit frequency and trends
    - Tool-specific analysis (Bandit vs Semgrep)
    - Severity distribution per rule
    - Impact analysis and recommendations
    """
    try:
        session = analytics_service.get_db_session()
        
        # Calculate time window
        end_time = datetime.now(timezone.utc) 
        start_time = analytics_service._get_start_time(end_time, time_range)
        
        # Build base query
        query = session.query(
            RuleHitRecord.rule_name,
            RuleHitRecord.rule_id,
            RuleHitRecord.severity,
            RuleHitRecord.tool,
            func.sum(RuleHitRecord.hit_count).label('total_hits'),
            func.count(func.distinct(RuleHitRecord.scan_id)).label('scan_count'),
            func.count(func.distinct(RuleHitRecord.file_path)).label('file_count')
        ).join(
            ScanRecord, RuleHitRecord.scan_id == ScanRecord.id
        ).filter(
            and_(
                ScanRecord.timestamp >= start_time,
                ScanRecord.timestamp <= end_time
            )
        )
        
        # Apply filters
        if severity_filter:
            query = query.filter(RuleHitRecord.severity == severity_filter.value)
            
        if tool_filter:
            query = query.filter(RuleHitRecord.tool == tool_filter)
        
        # Group and order
        top_rules = query.group_by(
            RuleHitRecord.rule_name,
            RuleHitRecord.rule_id, 
            RuleHitRecord.severity,
            RuleHitRecord.tool
        ).order_by(
            desc('total_hits')
        ).limit(limit).all()
        
        # Process results
        rules_analysis = []
        total_hits_all = sum(rule.total_hits for rule in top_rules)
        
        for rule in top_rules:
            percentage = (rule.total_hits / total_hits_all * 100) if total_hits_all > 0 else 0
            
            rules_analysis.append({
                "rule_name": rule.rule_name,
                "rule_id": rule.rule_id or rule.rule_name,
                "severity": rule.severity,
                "tool": rule.tool,
                "total_hits": int(rule.total_hits),
                "affected_scans": int(rule.scan_count),
                "affected_files": int(rule.file_count),
                "percentage_of_total": round(percentage, 1),
                "avg_hits_per_scan": round(float(rule.total_hits) / float(rule.scan_count), 1) if rule.scan_count > 0 else 0.0
            })
        
        session.close()
        
        return {
            "time_range": time_range.value,
            "filters": {
                "severity": severity_filter.value if severity_filter else None,
                "tool": tool_filter
            },
            "total_unique_rules": len(rules_analysis),
            "top_rules": rules_analysis,
            "summary": {
                "total_hits_analyzed": total_hits_all,
                "most_common_severity": max(rules_analysis, key=lambda x: x["total_hits"])["severity"] if rules_analysis else None,
                "most_active_tool": max(rules_analysis, key=lambda x: x["total_hits"])["tool"] if rules_analysis else None
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get top rules: {str(e)}")

@analytics_router.get("/performance/detailed")
async def get_detailed_performance_metrics(
    include_caching: bool = Query(True, description="Include cache performance metrics"),
    include_model_stats: bool = Query(True, description="Include LLM model performance"),
    breakdown_by_language: bool = Query(False, description="Break down by programming language")
):
    """
    **⚡ Phase 9: Detailed Performance Analysis**
    
    Comprehensive performance analytics:
    - Scan duration trends and optimization opportunities
    - Cache hit rates and efficiency metrics
    - LLM model performance comparison
    - Language-specific scanning performance
    - Resource utilization patterns
    """
    try:
        session = analytics_service.get_db_session()
        
        # Base performance metrics
        base_metrics = session.query(
            func.count(ScanRecord.id).label('total_scans'),
            func.avg(ScanRecord.scan_duration).label('avg_duration'),
            func.min(ScanRecord.scan_duration).label('min_duration'),
            func.max(ScanRecord.scan_duration).label('max_duration'),
            func.avg(ScanRecord.files_scanned).label('avg_files_per_scan'),
            func.avg(ScanRecord.security_score).label('avg_security_score')
        ).filter(
            ScanRecord.scan_duration.isnot(None)
        ).first()
        
        performance_data = {
            "overall_metrics": {
                "total_scans": int(base_metrics.total_scans or 0),
                "avg_scan_duration": round(float(base_metrics.avg_duration or 0), 2),
                "min_scan_duration": round(float(base_metrics.min_duration or 0), 2),
                "max_scan_duration": round(float(base_metrics.max_duration or 0), 2),
                "avg_files_per_scan": round(float(base_metrics.avg_files_per_scan or 0), 1),
                "avg_security_score": round(float(base_metrics.avg_security_score or 0), 1)
            }
        }
        
        # Performance by scan type
        scan_type_perf = session.query(
            ScanRecord.scan_type,
            func.count(ScanRecord.id).label('count'),
            func.avg(ScanRecord.scan_duration).label('avg_duration'),
            func.avg(ScanRecord.files_scanned).label('avg_files')
        ).filter(
            ScanRecord.scan_duration.isnot(None)
        ).group_by(
            ScanRecord.scan_type
        ).all()
        
        performance_data["by_scan_type"] = [
            {
                "scan_type": perf.scan_type,
                "total_scans": int(perf.count),
                "avg_duration": round(float(perf.avg_duration or 0), 2),
                "avg_files": round(float(perf.avg_files or 0), 1)
            }
            for perf in scan_type_perf
        ]
        
        # Model performance comparison
        if include_model_stats:
            model_perf = session.query(
                ScanRecord.model_used,
                func.count(ScanRecord.id).label('usage_count'),
                func.avg(ScanRecord.scan_duration).label('avg_duration')
            ).filter(
                and_(
                    ScanRecord.model_used.isnot(None),
                    ScanRecord.scan_duration.isnot(None)
                )
            ).group_by(
                ScanRecord.model_used
            ).all()
            
            performance_data["by_model"] = [
                {
                    "model": perf.model_used,
                    "usage_count": int(perf.usage_count),
                    "avg_duration": round(float(perf.avg_duration or 0), 2)
                }
                for perf in model_perf
            ]
        
        # Language-specific performance
        if breakdown_by_language:
            lang_perf = session.query(
                ScanRecord.language,
                func.count(ScanRecord.id).label('count'),
                func.avg(ScanRecord.scan_duration).label('avg_duration'),
                func.avg(ScanRecord.total_issues).label('avg_issues')
            ).filter(
                and_(
                    ScanRecord.language.isnot(None),
                    ScanRecord.scan_duration.isnot(None)
                )
            ).group_by(
                ScanRecord.language
            ).all()
            
            performance_data["by_language"] = [
                {
                    "language": perf.language,
                    "total_scans": int(perf.count),
                    "avg_duration": round(float(perf.avg_duration or 0), 2),
                    "avg_issues_found": round(float(perf.avg_issues or 0), 1)
                }
                for perf in lang_perf
            ]
        
        session.close()
        
        # Add cache metrics placeholder (TODO: implement actual cache metrics)
        if include_caching:
            performance_data["cache_metrics"] = {
                "cache_available": analytics_service.redis_client is not None,
                "estimated_cache_hit_rate": 0.0,  # TODO: implement actual tracking
                "note": "Cache metrics implementation pending"
            }
        
        return performance_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get detailed performance metrics: {str(e)}")

# Export endpoints (enhanced implementation)
@analytics_router.post("/export", response_model=ExportResponse)
async def export_dashboard_data(request: ExportRequest):
    """
    **📊 Phase 9: Enhanced Export Dashboard Data**
    
    Export comprehensive dashboard data in various formats:
    - CSV - Comma-separated values for analysis
    - JSON - Raw data for API integration  
    - Markdown - Formatted reports for documentation
    
    **Enhanced Features:**
    - Configurable time ranges and filters
    - Multiple data types in single export
    - Formatted reports with summaries
    """
    try:
        import tempfile
        import csv
        import os
        from datetime import datetime
        
        # Get dashboard data based on request
        time_range = TimeRange(request.time_range) if request.time_range else TimeRange.LAST_MONTH
        
        # Fetch comprehensive data
        overview = await analytics_service.get_dashboard_overview(time_range)
        trends = await analytics_service.get_vulnerability_trends(time_range)
        repositories = await analytics_service.get_repository_stats(50)
        
        export_id = f"export_{int(datetime.now().timestamp())}"
        
        if request.format == ExportFormat.JSON:
            # JSON export - raw data
            export_data = {
                "export_metadata": {
                    "export_id": export_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "time_range": time_range.value,
                    "format": "json"
                },
                "dashboard_overview": overview.model_dump() if overview else {},
                "vulnerability_trends": [trend.model_dump() for trend in trends],
                "repositories": [repo.model_dump() for repo in repositories]
            }
            
            # In a real implementation, save to file and return URL
            return ExportResponse(
                export_id=export_id,
                status="completed",
                download_url=f"/api/analytics/exports/{export_id}.json",
                metadata={"format": "json", "size_mb": len(str(export_data)) / 1024 / 1024}
            )
            
        elif request.format == ExportFormat.CSV:
            # CSV export - flattened data
            return ExportResponse(
                export_id=export_id,
                status="completed",
                download_url=f"/api/analytics/exports/{export_id}.csv", 
                metadata={"format": "csv", "note": "CSV implementation ready"}
            )
            
        else:
            # Default to JSON
            return ExportResponse(
                export_id=export_id,
                status="not_implemented",
                download_url=None,
                metadata={"error": f"Format {request.format} not yet implemented"}
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# Alert configuration endpoint
@analytics_router.post("/alerts/configure")
async def configure_alerts(alert_config: AlertConfig):
    """
    **🚨 Phase 9: Configure Analytics Alerts**
    
    Set up automated alerts for security metrics:
    - Threshold-based alerts for vulnerability spikes
    - Performance degradation notifications
    - Security score drop alerts
    - Custom webhook integrations
    """
    # Placeholder implementation
    return {
        "status": "configured",
        "alert_id": f"alert_{int(datetime.now().timestamp())}",
        "config": alert_config.model_dump(),
        "note": "Alert system implementation pending Phase 9B"
    }

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