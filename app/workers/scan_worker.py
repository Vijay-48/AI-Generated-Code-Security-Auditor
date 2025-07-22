"""
Celery Workers for AI Code Security Auditor
Handles async processing of security scans and LLM analysis
"""
import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from celery import current_task
from celery.signals import worker_init, worker_shutdown

from app.celery_app import celery_app
from app.agents.security_agent import SecurityAgent
from app.services.cache_service import cache_service
from app.websocket_manager import websocket_manager
from app.config import settings


# Global cache for worker initialization
_worker_initialized = False

async def _publish_progress_update(job_id: str, progress_data: Dict[str, Any]):
    """Helper function to publish progress updates via Redis directly"""
    try:
        import redis.asyncio as redis
        from app.config import settings
        
        # Create a simple Redis publisher (don't reuse websocket_manager)
        redis_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}"
        redis_publisher = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
        
        channel = f"job_progress:{job_id}"
        message = json.dumps({
            "job_id": job_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **progress_data
        })
        
        await redis_publisher.publish(channel, message)
        await redis_publisher.close()
        
    except Exception as e:
        # Don't fail the job if publishing fails
        print(f"⚠️ Failed to publish progress update for job {job_id}: {e}")

@worker_init.connect
def init_worker(**kwargs):
    """Initialize worker with cache connections"""
    global _worker_initialized
    print("🚀 Initializing Celery worker...")
    
    # Initialize async event loop for worker
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Connect to cache only (no WebSocket manager in worker)
    loop.run_until_complete(cache_service.connect())
    
    _worker_initialized = True
    print("✅ Worker initialized successfully")


@worker_shutdown.connect  
def shutdown_worker(**kwargs):
    """Cleanup worker resources"""
    print("🔄 Shutting down Celery worker...")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(cache_service.disconnect())
    except Exception as e:
        print(f"⚠️ Error during worker shutdown: {e}")
    print("✅ Worker shutdown complete")


@celery_app.task(bind=True, name='app.workers.scan_worker.process_security_scan')
def process_security_scan(
    self,
    job_id: str,
    code: str,
    language: str,
    filename: str = "",
    preferred_model: Optional[str] = None,
    use_advanced_analysis: bool = False,
    cache_enabled: bool = True
) -> Dict[str, Any]:
    """
    Process security scan asynchronously
    
    Args:
        job_id: Unique job identifier for progress tracking
        code: Source code to analyze
        language: Programming language
        filename: Optional filename for context
        preferred_model: Optional preferred LLM model
        use_advanced_analysis: Enable advanced multi-model analysis
        cache_enabled: Enable caching for this scan
        
    Returns:
        Dict with scan results and metadata
    """
    
    def run_async_scan():
        """Run the async scan in the worker's event loop"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            _async_process_security_scan(
                self, job_id, code, language, filename, 
                preferred_model, use_advanced_analysis, cache_enabled
            )
        )
    
    return run_async_scan()


async def _async_process_security_scan(
    task,
    job_id: str,
    code: str, 
    language: str,
    filename: str,
    preferred_model: Optional[str],
    use_advanced_analysis: bool,
    cache_enabled: bool
) -> Dict[str, Any]:
    """Async implementation of security scan processing"""
    
    start_time = datetime.now(timezone.utc)
    
    try:
        # Update job progress - Starting
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'initializing',
            'progress': 0,
            'message': 'Starting security analysis...',
            'started_at': start_time.isoformat()
        })
        
        # Publish WebSocket update
        await _publish_progress_update(job_id, {
            'status': 'processing',
            'stage': 'initializing', 
            'progress': 0,
            'message': 'Starting security analysis...',
            'started_at': start_time.isoformat()
        })
        
        # Check cache first
        cache_hit = False
        if cache_enabled:
            tools_config = {
                'language': language,
                'preferred_model': preferred_model,
                'use_advanced_analysis': use_advanced_analysis
            }
            
            cached_results = await cache_service.get_scan_results(code, language, tools_config)
            if cached_results:
                await cache_service.set_job_progress(job_id, {
                    'status': 'completed',
                    'stage': 'cache_hit',
                    'progress': 100,
                    'message': 'Results retrieved from cache',
                    'completed_at': datetime.now(timezone.utc).isoformat(),
                    'cache_hit': True,
                    'execution_time': 0.1
                })
                
                # WebSocket update for cache hit
                await _publish_progress_update(job_id, {
                    'status': 'completed',
                    'stage': 'cache_hit',
                    'progress': 100,
                    'message': 'Results retrieved from cache',
                    'completed_at': datetime.now(timezone.utc).isoformat(),
                    'cache_hit': True,
                    'execution_time': 0.1
                })
                return {
                    'job_id': job_id,
                    'status': 'completed',
                    'results': cached_results,
                    'metadata': {
                        'cache_hit': True,
                        'execution_time': 0.1,
                        'started_at': start_time.isoformat(),
                        'completed_at': datetime.now(timezone.utc).isoformat()
                    }
                }
        
        # Progress: Scanning
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'scanning',
            'progress': 10,
            'message': 'Running security scanners...'
        })
        await _publish_progress_update(job_id, {
            'status': 'processing',
            'stage': 'scanning',
            'progress': 10,
            'message': 'Running security scanners...'
        })
        
        # Create fresh security agent
        agent = SecurityAgent()
        
        # Progress: Vulnerability Analysis
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'vulnerability_analysis',
            'progress': 25,
            'message': 'Analyzing vulnerabilities...'
        })
        await _publish_progress_update(job_id, {
            'status': 'processing',
            'stage': 'vulnerability_analysis',
            'progress': 25,
            'message': 'Analyzing vulnerabilities...'
        })
        
        # Progress: Remediation Retrieval
        await cache_service.set_job_progress(job_id, {
            'status': 'processing', 
            'stage': 'remediation_retrieval',
            'progress': 40,
            'message': 'Retrieving remediation patterns...'
        })
        await _publish_progress_update(job_id, {
            'status': 'processing', 
            'stage': 'remediation_retrieval',
            'progress': 40,
            'message': 'Retrieving remediation patterns...'
        })
        
        # Progress: AI Analysis
        if use_advanced_analysis or preferred_model:
            await cache_service.set_job_progress(job_id, {
                'status': 'processing',
                'stage': 'ai_analysis', 
                'progress': 60,
                'message': 'Running AI analysis and patch generation...'
            })
            await _publish_progress_update(job_id, {
                'status': 'processing',
                'stage': 'ai_analysis', 
                'progress': 60,
                'message': 'Running AI analysis and patch generation...'
            })
        
        # Run the security analysis
        results = await agent.run(
            code=code,
            language=language,
            filename=filename,
            preferred_model=preferred_model,
            use_advanced_analysis=use_advanced_analysis
        )
        
        # Progress: Finalizing
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'finalizing',
            'progress': 90,
            'message': 'Finalizing results...'
        })
        await _publish_progress_update(job_id, {
            'status': 'processing',
            'stage': 'finalizing',
            'progress': 90,
            'message': 'Finalizing results...'
        })
        
        # Cache results if enabled
        if cache_enabled:
            tools_config = {
                'language': language,
                'preferred_model': preferred_model,
                'use_advanced_analysis': use_advanced_analysis
            }
            await cache_service.cache_scan_results(code, language, tools_config, results)
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        # Final progress update - Completed
        await cache_service.set_job_progress(job_id, {
            'status': 'completed',
            'stage': 'completed',
            'progress': 100,
            'message': f'Analysis completed in {execution_time:.1f}s',
            'completed_at': end_time.isoformat(),
            'cache_hit': False,
            'execution_time': execution_time,
            'vulnerabilities_found': len(results.get('vulnerabilities', [])),
            'patches_generated': len(results.get('patches', [])),
        })
        await _publish_progress_update(job_id, {
            'status': 'completed',
            'stage': 'completed',
            'progress': 100,
            'message': f'Analysis completed in {execution_time:.1f}s',
            'completed_at': end_time.isoformat(),
            'cache_hit': False,
            'execution_time': execution_time,
            'vulnerabilities_found': len(results.get('vulnerabilities', [])),
            'patches_generated': len(results.get('patches', [])),
        })
        
        return {
            'job_id': job_id,
            'status': 'completed',
            'results': results,
            'metadata': {
                'cache_hit': False,
                'execution_time': execution_time,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'vulnerabilities_found': len(results.get('vulnerabilities', [])),
                'patches_generated': len(results.get('patches', [])),
                'advanced_analysis': use_advanced_analysis,
                'model_used': preferred_model
            }
        }
        
    except Exception as e:
        # Handle errors and update job progress
        error_time = datetime.now(timezone.utc)
        execution_time = (error_time - start_time).total_seconds()
        
        await cache_service.set_job_progress(job_id, {
            'status': 'failed',
            'stage': 'error',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}',
            'error': str(e),
            'failed_at': error_time.isoformat(),
            'execution_time': execution_time
        })
        await _publish_progress_update(job_id, {
            'status': 'failed',
            'stage': 'error',
            'progress': 0,
            'message': f'Analysis failed: {str(e)}',
            'error': str(e),
            'failed_at': error_time.isoformat(),
            'execution_time': execution_time
        })
        
        # Re-raise for Celery error handling
        raise Exception(f"Security scan failed: {str(e)}")


@celery_app.task(bind=True, name='app.workers.scan_worker.process_llm_analysis')  
def process_llm_analysis(
    self,
    job_id: str,
    operation_type: str,
    model: str,
    content: str,
    context: Dict[str, Any],
    cache_enabled: bool = True
) -> Dict[str, Any]:
    """
    Process individual LLM analysis requests
    
    Args:
        job_id: Job identifier
        operation_type: Type of LLM operation (patch_generation, assessment, etc.)
        model: LLM model to use  
        content: Content to analyze
        context: Additional context for the operation
        cache_enabled: Enable caching for this request
        
    Returns:
        Dict with LLM response and metadata
    """
    
    def run_async_llm():
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            _async_process_llm_analysis(
                self, job_id, operation_type, model, content, context, cache_enabled
            )
        )
    
    return run_async_llm()


async def _async_process_llm_analysis(
    task,
    job_id: str,
    operation_type: str,
    model: str,
    content: str, 
    context: Dict[str, Any],
    cache_enabled: bool
) -> Dict[str, Any]:
    """Async implementation of LLM analysis"""
    
    start_time = datetime.now(timezone.utc)
    
    try:
        # Check cache first
        if cache_enabled:
            cached_response = await cache_service.get_llm_response(model, content, operation_type)
            if cached_response:
                return {
                    'job_id': job_id,
                    'status': 'completed',
                    'response': cached_response,
                    'metadata': {
                        'cache_hit': True,
                        'execution_time': 0.05,
                        'model_used': model,
                        'operation_type': operation_type
                    }
                }
        
        # Import LLM service (done here to avoid circular imports)
        from app.services.llm_service import LLMService
        llm_service = LLMService()
        
        # Process based on operation type
        if operation_type == 'patch_generation':
            response = await llm_service.generate_fix_diff(
                content,
                context.get('vulnerability', {}),
                context.get('remediation_pattern', {})
            )
        elif operation_type == 'assessment':
            response = await llm_service.assess_fix_quality(
                context.get('original_code', ''),
                content,
                context.get('vulnerability', {})
            )
        elif operation_type == 'classification':
            response = await llm_service.classify_vulnerability_fast(
                content,
                context.get('vulnerability', {})
            )
        elif operation_type == 'explanation':
            response = await llm_service.explain_vulnerability(
                content,
                context.get('vulnerability', {})
            )
        else:
            raise ValueError(f"Unknown operation type: {operation_type}")
        
        # Cache successful response
        if cache_enabled and 'error' not in response:
            await cache_service.cache_llm_response(model, content, operation_type, response)
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'job_id': job_id,
            'status': 'completed',
            'response': response,
            'metadata': {
                'cache_hit': False,
                'execution_time': execution_time,
                'model_used': model,
                'operation_type': operation_type,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat()
            }
        }
        
    except Exception as e:
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        return {
            'job_id': job_id,
            'status': 'failed',
            'error': str(e),
            'metadata': {
                'execution_time': execution_time,
                'model_used': model,
                'operation_type': operation_type,
                'failed_at': end_time.isoformat()
            }
        }


@celery_app.task(name='app.workers.scan_worker.get_job_status')
def get_job_status(job_id: str) -> Dict[str, Any]:
    """Get current job status and progress"""
    
    def run_async_status():
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(_async_get_job_status(job_id))
    
    return run_async_status()


async def _async_get_job_status(job_id: str) -> Dict[str, Any]:
    """Async implementation of job status retrieval"""
    try:
        progress = await cache_service.get_job_progress(job_id)
        if progress:
            return {
                'job_id': job_id,
                'found': True,
                **progress
            }
        else:
            return {
                'job_id': job_id,
                'found': False,
                'status': 'not_found',
                'message': 'Job not found or expired'
            }
    except Exception as e:
        return {
            'job_id': job_id,
            'found': False,
            'status': 'error',
            'error': str(e)
        }