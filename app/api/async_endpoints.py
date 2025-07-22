"""
Async API endpoints for AI Code Security Auditor
Provides async job processing with real-time progress tracking
"""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, field_validator

from app.workers.scan_worker import process_security_scan, get_job_status, process_llm_analysis
from app.workers.repo_scan_worker import process_bulk_repository_scan
from app.services.cache_service import cache_service
from app.services.llm_client import get_available_models
from app.websocket_manager import websocket_manager

# Create router for async endpoints
async_router = APIRouter(prefix="/async", tags=["Async Operations"])

@async_router.websocket("/jobs/{job_id}/ws")
async def websocket_job_progress_new(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates
    
    Clients can connect to receive live progress updates as jobs execute
    Features:
    - Real-time progress streaming
    - Automatic heartbeat to keep connections alive
    - Error handling and graceful disconnection
    - Multiple clients can connect to the same job
    """
    
    client_info = {
        "user_agent": websocket.headers.get("user-agent", "unknown"),
        "origin": websocket.headers.get("origin", "unknown")
    }
    
    await websocket_manager.connect(websocket, job_id, client_info)
    
    try:
        # Send initial job status if available
        progress = await cache_service.get_job_progress(job_id)
        if progress:
            await websocket.send_json({
                "type": "initial_status",
                "job_id": job_id,
                **progress
            })
        else:
            await websocket.send_json({
                "type": "initial_status",
                "job_id": job_id,
                "status": "unknown",
                "message": "Job status not found. Job may be queued or expired."
            })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                # Wait for client message with timeout for heartbeat
                data = await asyncio.wait_for(websocket.receive_json(), timeout=30.0)
                
                # Handle client requests
                if data.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "job_id": job_id,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    })
                
                elif data.get("type") == "get_status":
                    # Send current job status
                    progress = await cache_service.get_job_progress(job_id)
                    if progress:
                        await websocket.send_json({
                            "type": "status_update",
                            "job_id": job_id,
                            **progress
                        })
                
            except asyncio.TimeoutError:
                # Send heartbeat if no client activity
                await websocket_manager.send_heartbeat(job_id)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, job_id)
    except Exception as e:
        print(f"⚠️ WebSocket error for job {job_id}: {e}")
        await websocket.send_json({
            "type": "error",
            "job_id": job_id,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        websocket_manager.disconnect(websocket, job_id)

# Remove the old ConnectionManager class since we're using websocket_manager now

# Request models
class AsyncAuditRequest(BaseModel):
    code: str
    language: str
    filename: Optional[str] = None
    model: Optional[str] = None
    use_advanced_analysis: Optional[bool] = False
    cache_enabled: Optional[bool] = True
    priority: Optional[str] = "normal"  # normal, high, urgent
    
    @field_validator('code')
    @classmethod
    def code_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Code cannot be empty')
        return v
    
    @field_validator('language')
    @classmethod
    def language_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Language cannot be empty')
        valid_languages = ['python', 'javascript', 'java', 'go']
        if v.lower() not in valid_languages:
            raise ValueError(f'Language must be one of: {valid_languages}')
        return v.lower()
    
    @field_validator('model')
    @classmethod
    def model_must_be_valid(cls, v):
        if v is None:
            return v
        available_models = get_available_models()
        if v not in available_models:
            raise ValueError(f'Model must be one of: {available_models}')
        return v
    
    @field_validator('priority')
    @classmethod
    def priority_must_be_valid(cls, v):
        if v is None:
            return "normal"
        valid_priorities = ['normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

class LLMAnalysisRequest(BaseModel):
    operation_type: str  # patch_generation, assessment, classification, explanation
    model: str
    content: str
    context: Dict[str, Any]
    cache_enabled: Optional[bool] = True
    
    @field_validator('operation_type')
    @classmethod
    def operation_type_must_be_valid(cls, v):
        valid_types = ['patch_generation', 'assessment', 'classification', 'explanation']
        if v not in valid_types:
            raise ValueError(f'Operation type must be one of: {valid_types}')
        return v

class BulkRepositoryRequest(BaseModel):
    repository_url: str
    branch: Optional[str] = "main"
    commit: Optional[str] = None
    include_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    max_files: Optional[int] = 500
    batch_size: Optional[int] = 10
    use_advanced_analysis: Optional[bool] = False
    cache_enabled: Optional[bool] = True
    priority: Optional[str] = "normal"
    
    @field_validator('repository_url')
    @classmethod
    def repository_url_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Repository URL cannot be empty')
        return v.strip()
    
    @field_validator('branch')
    @classmethod
    def branch_must_be_valid(cls, v):
        if v and not v.strip():
            raise ValueError('Branch name cannot be empty')
        return v or "main"
    
    @field_validator('max_files')
    @classmethod
    def max_files_must_be_reasonable(cls, v):
        if v is not None and (v < 1 or v > 2000):
            raise ValueError('max_files must be between 1 and 2000')
        return v or 500
    
    @field_validator('batch_size')
    @classmethod
    def batch_size_must_be_reasonable(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError('batch_size must be between 1 and 100')
        return v or 10
    
    @field_validator('priority')
    @classmethod
    def priority_must_be_valid(cls, v):
        if v is None:
            return "normal"
        valid_priorities = ['normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {valid_priorities}')
        return v

# Response models
class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str
    estimated_duration: Optional[str] = None
    progress_url: Optional[str] = None
    websocket_url: Optional[str] = None

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    stage: Optional[str] = None
    progress: Optional[int] = None
    message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    failed_at: Optional[str] = None
    execution_time: Optional[float] = None
    cache_hit: Optional[bool] = None
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@async_router.post("/audit", response_model=JobResponse)
async def submit_audit_job(request: AsyncAuditRequest):
    """
    Submit security audit job for async processing
    
    Returns job ID for tracking progress and retrieving results
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Determine queue based on priority
        queue_mapping = {
            'urgent': 'urgent_scans',
            'high': 'high_priority_scans', 
            'normal': 'security_scans'
        }
        queue = queue_mapping.get(request.priority, 'security_scans')
        
        # Submit job to Celery
        task = process_security_scan.apply_async(
            args=[
                job_id,
                request.code,
                request.language,
                request.filename or "",
                request.model,
                request.use_advanced_analysis,
                request.cache_enabled
            ],
            queue=queue,
            task_id=job_id
        )
        
        # Estimate duration based on code complexity and analysis type
        code_size = len(request.code)
        if request.use_advanced_analysis:
            estimated_duration = "2-5 minutes"
        elif code_size > 5000:
            estimated_duration = "1-3 minutes" 
        else:
            estimated_duration = "30-90 seconds"
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message="Security audit job queued successfully",
            estimated_duration=estimated_duration,
            progress_url=f"/async/jobs/{job_id}/status",
            websocket_url=f"/async/jobs/{job_id}/progress"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")

@async_router.post("/llm-analysis", response_model=JobResponse)
async def submit_llm_analysis_job(request: LLMAnalysisRequest):
    """
    Submit individual LLM analysis job for async processing
    
    Useful for specific AI operations like patch generation or vulnerability explanations
    """
    try:
        job_id = str(uuid.uuid4())
        
        task = process_llm_analysis.apply_async(
            args=[
                job_id,
                request.operation_type,
                request.model,
                request.content,
                request.context,
                request.cache_enabled
            ],
            queue='llm_analysis',
            task_id=job_id
        )
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message=f"LLM {request.operation_type} job queued successfully",
            estimated_duration="30-60 seconds",
            progress_url=f"/async/jobs/{job_id}/status",
            websocket_url=f"/async/jobs/{job_id}/progress"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit LLM job: {str(e)}")

@async_router.post("/repo-scan", response_model=JobResponse)
async def submit_bulk_repository_scan_job(request: BulkRepositoryRequest):
    """
    🚀 **NEW in Phase 6**: Submit bulk repository scan job for async processing
    
    **Bulk Repository Scanning Features:**
    - Git repository cloning and analysis
    - Batch processing with real-time progress updates  
    - File-level vulnerability detection and caching
    - Aggregated repository security reports
    - Support for custom include/exclude patterns
    
    **Parameters:**
    - **repository_url**: Git repository URL or local path
    - **branch**: Git branch to scan (default: main)
    - **commit**: Specific commit hash (optional)
    - **include_patterns**: File patterns to include (e.g., ["*.py", "*.js"])
    - **exclude_patterns**: File patterns to exclude (e.g., ["*/tests/*"])
    - **max_files**: Maximum files to scan (1-2000, default: 500)
    - **batch_size**: Files per batch (1-100, default: 10) 
    - **use_advanced_analysis**: Enable multi-model AI analysis
    - **cache_enabled**: Enable file-level result caching
    - **priority**: Job priority (normal, high, urgent)
    
    **Returns:**
    - Job ID for progress tracking via WebSocket
    - Estimated duration based on repository size
    - URLs for status checking and result retrieval
    
    **Example:**
    ```json
    {
        "repository_url": "https://github.com/user/repo.git",
        "branch": "main",
        "max_files": 100,
        "use_advanced_analysis": true
    }
    ```
    """
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Determine queue based on priority
        queue_mapping = {
            'urgent': 'urgent_scans',
            'high': 'high_priority_scans', 
            'normal': 'security_scans'
        }
        queue = queue_mapping.get(request.priority, 'security_scans')
        
        # Submit bulk repository scan job to Celery
        task = process_bulk_repository_scan.apply_async(
            args=[
                job_id,
                request.repository_url,
                request.branch,
                request.commit,
                request.include_patterns,
                request.exclude_patterns,
                request.max_files,
                request.batch_size,
                request.use_advanced_analysis,
                request.cache_enabled
            ],
            queue=queue,
            task_id=job_id
        )
        
        # Estimate duration based on configuration
        base_time_per_file = 2 if request.use_advanced_analysis else 1  # seconds
        estimated_total_seconds = (request.max_files or 500) * base_time_per_file
        
        if estimated_total_seconds < 60:
            estimated_duration = f"{estimated_total_seconds}s"
        elif estimated_total_seconds < 3600:
            estimated_duration = f"{estimated_total_seconds // 60}-{(estimated_total_seconds // 60) + 2} minutes"
        else:
            estimated_duration = f"{estimated_total_seconds // 3600}-{(estimated_total_seconds // 3600) + 1} hours"
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message=f"Bulk repository scan queued successfully for {request.repository_url}",
            estimated_duration=estimated_duration,
            progress_url=f"/async/jobs/{job_id}/status",
            websocket_url=f"/async/jobs/{job_id}/ws"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit repository scan job: {str(e)}")

@async_router.get("/jobs/{job_id}/status", response_model=JobStatusResponse) 
async def get_job_status_endpoint(job_id: str):
    """
    Get current job status and progress
    
    Returns detailed progress information including stage, percentage complete, and results
    """
    try:
        # Get job progress from cache
        progress = await cache_service.get_job_progress(job_id)
        
        if not progress:
            # Check if it's a completed Celery task
            from celery.result import AsyncResult
            result = AsyncResult(job_id)
            
            if result.state == 'SUCCESS':
                task_result = result.get()
                return JobStatusResponse(
                    job_id=job_id,
                    status='completed',
                    stage='completed',
                    progress=100,
                    message='Job completed successfully',
                    results=task_result.get('results'),
                    metadata=task_result.get('metadata'),
                    completed_at=task_result.get('metadata', {}).get('completed_at')
                )
            elif result.state == 'FAILURE':
                return JobStatusResponse(
                    job_id=job_id,
                    status='failed',
                    stage='error',
                    progress=0,
                    message='Job failed',
                    error=str(result.info),
                    failed_at=datetime.now(timezone.utc).isoformat()
                )
            elif result.state == 'PENDING':
                return JobStatusResponse(
                    job_id=job_id,
                    status='queued',
                    stage='queued',
                    progress=0,
                    message='Job is queued for processing'
                )
            else:
                return JobStatusResponse(
                    job_id=job_id,
                    status=result.state.lower(),
                    message=f'Job state: {result.state}'
                )
        
        # Create response from progress data, avoiding duplicate job_id
        response_data = {k: v for k, v in progress.items() if k != 'job_id'}
        response_data['job_id'] = job_id
        
        return JobStatusResponse(**response_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job status: {str(e)}")

@async_router.get("/jobs/{job_id}/results")
async def get_job_results(job_id: str):
    """
    Get completed job results
    
    Returns full audit results once job is completed
    """
    try:
        # First check cache for progress
        progress = await cache_service.get_job_progress(job_id)
        
        if progress and progress.get('status') == 'completed':
            # Get results from Celery if needed
            from celery.result import AsyncResult
            result = AsyncResult(job_id)
            
            if result.successful():
                task_result = result.get()
                return {
                    "job_id": job_id,
                    "status": "completed", 
                    "results": task_result.get('results'),
                    "metadata": task_result.get('metadata')
                }
        
        # Job not completed yet
        status = progress.get('status', 'unknown') if progress else 'not_found'
        raise HTTPException(
            status_code=202 if status in ['queued', 'processing'] else 404,
            detail=f"Job {status}. Results not available yet." if status != 'not_found' else "Job not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job results: {str(e)}")

@async_router.delete("/jobs/{job_id}")
async def cancel_job(job_id: str):
    """
    Cancel a queued or running job
    """
    try:
        from celery.result import AsyncResult
        result = AsyncResult(job_id)
        
        if result.state in ['PENDING', 'STARTED']:
            result.revoke(terminate=True)
            
            # Update job progress to cancelled
            await cache_service.set_job_progress(job_id, {
                'status': 'cancelled',
                'stage': 'cancelled',
                'progress': 0,
                'message': 'Job cancelled by user',
                'cancelled_at': datetime.now(timezone.utc).isoformat()
            })
            
            return {"job_id": job_id, "status": "cancelled", "message": "Job cancelled successfully"}
        else:
            raise HTTPException(status_code=400, detail=f"Cannot cancel job in state: {result.state}")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel job: {str(e)}")

@async_router.websocket("/jobs/{job_id}/progress")
async def websocket_job_progress(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time job progress updates
    
    Clients can connect to receive live progress updates as jobs execute
    """
    await websocket_manager.connect(websocket, job_id, {})
    try:
        while True:
            # Get current progress
            progress = await cache_service.get_job_progress(job_id)
            
            if progress:
                await websocket.send_json({
                    "type": "progress",
                    "job_id": job_id,
                    **progress
                })
                
                # If job is completed, send final update and close
                if progress.get('status') in ['completed', 'failed', 'cancelled']:
                    await websocket.send_json({
                        "type": "completion",
                        "job_id": job_id,
                        "final_status": progress.get('status')
                    })
                    break
            
            # Wait before next update
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, job_id)
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "job_id": job_id,
            "error": str(e)
        })
        websocket_manager.disconnect(websocket, job_id)

@async_router.get("/jobs")
async def list_jobs(
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, description="Maximum number of jobs to return"),
    offset: int = Query(0, description="Number of jobs to skip")
):
    """
    List recent jobs with optional status filtering
    
    Useful for monitoring and debugging job processing
    """
    try:
        # Get job keys from cache
        if not cache_service.connected:
            raise HTTPException(status_code=503, detail="Cache service not available")
        
        job_keys = await cache_service.redis_client.keys("job:*")
        jobs = []
        
        for key in job_keys[offset:offset+limit]:
            job_data = await cache_service.redis_client.get(key)
            if job_data:
                job = json.loads(job_data)
                if not status or job.get('status') == status:
                    jobs.append(job)
        
        return {
            "jobs": jobs,
            "total": len(job_keys),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list jobs: {str(e)}")

@async_router.get("/cache/stats")
async def get_cache_statistics():
    """
    Get cache performance statistics
    
    Shows hit rates, storage usage, and cache health metrics
    """
    try:
        stats = await cache_service.get_cache_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache stats: {str(e)}")

@async_router.get("/websocket/stats")
async def get_websocket_stats():
    """
    Get WebSocket connection statistics
    
    Shows number of active connections, jobs being monitored, etc.
    """
    try:
        stats = websocket_manager.get_connection_stats()
        return {
            "websocket_stats": stats,
            "redis_status": "connected" if websocket_manager.redis_publisher else "disconnected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get WebSocket stats: {str(e)}")

@async_router.delete("/cache/clear")
async def clear_cache(cache_type: Optional[str] = Query(None, description="Type of cache to clear (scan, llm, patch, job)")):
    """
    Clear cache entries
    
    Useful for debugging and forcing fresh analysis
    """
    try:
        success = await cache_service.clear_cache(cache_type)
        if success:
            return {"message": f"Cache cleared successfully", "cache_type": cache_type or "all"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear cache")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")

