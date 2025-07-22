"""
Celery Configuration for AI Code Security Auditor
Handles async job processing for security scans
"""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "security_auditor",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.workers.scan_worker', 'app.workers.repo_scan_worker']
)

# Import task modules to ensure they're registered
from app.workers import scan_worker, repo_scan_worker

# Celery configuration
celery_app.conf.update(
    # Task routing
    task_routes={
        'app.workers.scan_worker.process_security_scan': {'queue': 'security_scans'},
        'app.workers.scan_worker.process_llm_analysis': {'queue': 'llm_analysis'},
        'app.workers.repo_scan_worker.process_bulk_repository_scan': {'queue': 'security_scans'},
    },
    
    # Task execution
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Worker configuration
    worker_prefetch_multiplier=1,  # Process one task at a time for memory efficiency
    task_acks_late=True,  # Acknowledge task after completion
    worker_max_tasks_per_child=1000,  # Restart workers to prevent memory leaks
    
    # Task timeouts
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,       # 10 minutes hard limit
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Retry configuration
    task_default_retry_delay=60,  # 1 minute retry delay
    task_max_retries=3,
    
    # Queue configuration
    task_default_queue='default',
    task_create_missing_queues=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Task annotations for better control
celery_app.conf.task_annotations = {
    'app.workers.scan_worker.process_security_scan': {
        'rate_limit': '10/m',  # Max 10 scans per minute
        'time_limit': 300,     # 5 minute timeout
    },
    'app.workers.scan_worker.process_llm_analysis': {
        'rate_limit': '30/m',  # Max 30 LLM calls per minute (due to API limits)
        'time_limit': 120,     # 2 minute timeout for LLM calls
    },
    'app.workers.repo_scan_worker.process_bulk_repository_scan': {
        'rate_limit': '5/m',   # Max 5 repository scans per minute
        'time_limit': 1800,    # 30 minute timeout for large repositories
    },
}

if __name__ == '__main__':
    celery_app.start()