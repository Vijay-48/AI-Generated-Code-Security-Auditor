"""
Bulk Repository Scanning Worker
Handles large-scale repository analysis with real-time progress updates
"""
import asyncio
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import asdict

from celery import current_task
from app.celery_app import celery_app
from app.services.git_service import git_service, RepositoryInfo, FileInfo
from app.services.cache_service import cache_service
from app.agents.security_agent import SecurityAgent
from app.config import settings
import redis.asyncio as redis

async def _publish_repo_progress_update(job_id: str, progress_data: Dict[str, Any]):
    """Helper function to publish repository scan progress updates via Redis"""
    try:
        # Create a simple Redis publisher for progress updates
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
        print(f"⚠️ Failed to publish repo progress update for job {job_id}: {e}")

@celery_app.task(bind=True, name='app.workers.repo_scan_worker.process_bulk_repository_scan')
def process_bulk_repository_scan(
    self,
    job_id: str,
    repository_url: str,
    branch: str = "main",
    commit: Optional[str] = None,
    include_patterns: Optional[List[str]] = None,
    exclude_patterns: Optional[List[str]] = None,
    max_files: int = 500,
    batch_size: int = 10,
    use_advanced_analysis: bool = False,
    cache_enabled: bool = True
) -> Dict[str, Any]:
    """
    Process bulk repository security scan
    
    Args:
        job_id: Unique job identifier
        repository_url: Git repository URL or local path
        branch: Git branch to scan (default: main)
        commit: Specific commit to scan (optional)
        include_patterns: File patterns to include
        exclude_patterns: File patterns to exclude
        max_files: Maximum number of files to scan
        batch_size: Number of files to process in each batch
        use_advanced_analysis: Enable advanced AI analysis
        cache_enabled: Enable result caching
    
    Returns:
        Dict with aggregated scan results and metadata
    """
    
    def run_async_repo_scan():
        """Run the async repository scan in the worker's event loop"""
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(
            _async_process_bulk_repository_scan(
                self, job_id, repository_url, branch, commit,
                include_patterns, exclude_patterns, max_files, batch_size,
                use_advanced_analysis, cache_enabled
            )
        )
    
    return run_async_repo_scan()

async def _async_process_bulk_repository_scan(
    task,
    job_id: str,
    repository_url: str,
    branch: str,
    commit: Optional[str],
    include_patterns: Optional[List[str]],
    exclude_patterns: Optional[List[str]],
    max_files: int,
    batch_size: int,
    use_advanced_analysis: bool,
    cache_enabled: bool
) -> Dict[str, Any]:
    """Async implementation of bulk repository scanning"""
    
    start_time = datetime.now(timezone.utc)
    repo_info = None
    
    try:
        # Initialize repository info
        repo_info = RepositoryInfo(
            url=repository_url,
            branch=branch,
            commit=commit,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            max_files=max_files
        )
        
        # Progress: Initializing
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'initializing',
            'progress': 0,
            'message': f'Initializing repository scan: {repository_url}',
            'started_at': start_time.isoformat(),
            'repository_url': repository_url,
            'branch': branch
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'processing',
            'stage': 'initializing',
            'progress': 0,
            'message': f'Initializing repository scan: {repository_url}',
            'repository_url': repository_url,
            'branch': branch
        })
        
        # Progress: Cloning repository
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'cloning',
            'progress': 5,
            'message': 'Cloning repository...'
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'processing',
            'stage': 'cloning',
            'progress': 5,
            'message': 'Cloning repository...'
        })
        
        # Clone repository
        repo_path = await git_service.clone_repository(repo_info)
        
        # Progress: Discovering files
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'discovery',
            'progress': 15,
            'message': 'Discovering scannable files...'
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'processing',
            'stage': 'discovery',
            'progress': 15,
            'message': 'Discovering scannable files...'
        })
        
        # Discover files
        discovered_files = await git_service.discover_files(repo_info, repo_path)
        
        if not discovered_files:
            raise Exception("No scannable files found in repository")
        
        # Get repository metadata
        repo_metadata = await git_service.get_repository_metadata(repo_path)
        
        # Progress: Starting file analysis
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'scanning',
            'progress': 20,
            'message': f'Starting analysis of {len(discovered_files)} files...',
            'total_files': len(discovered_files),
            'files_processed': 0
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'processing',
            'stage': 'scanning',
            'progress': 20,
            'message': f'Starting analysis of {len(discovered_files)} files...',
            'total_files': len(discovered_files),
            'files_processed': 0
        })
        
        # Process files in batches
        all_vulnerabilities = []
        all_patches = []
        file_results = {}
        files_processed = 0
        total_files = len(discovered_files)
        
        # Create security agent for scanning
        security_agent = SecurityAgent()
        
        # Process files in batches for better progress tracking
        for batch_start in range(0, len(discovered_files), batch_size):
            batch_end = min(batch_start + batch_size, len(discovered_files))
            batch_files = discovered_files[batch_start:batch_end]
            
            # Process current batch
            for file_info in batch_files:
                try:
                    # Progress update for current file
                    files_processed += 1
                    progress_percent = 20 + int((files_processed / total_files) * 60)  # 20-80% for file processing
                    
                    await cache_service.set_job_progress(job_id, {
                        'status': 'processing',
                        'stage': 'scanning',
                        'progress': progress_percent,
                        'message': f'Scanning {file_info.relative_path}...',
                        'total_files': total_files,
                        'files_processed': files_processed,
                        'current_file': file_info.relative_path
                    })
                    
                    await _publish_repo_progress_update(job_id, {
                        'status': 'processing',
                        'stage': 'scanning',
                        'progress': progress_percent,
                        'message': f'Scanning {file_info.relative_path}...',
                        'total_files': total_files,
                        'files_processed': files_processed,
                        'current_file': file_info.relative_path
                    })
                    
                    # Check cache for file-level results
                    cached_result = None
                    if cache_enabled:
                        cached_result = await cache_service.get_scan_results(
                            file_info.content_hash, 
                            file_info.language,
                            {'use_advanced_analysis': use_advanced_analysis}
                        )
                    
                    if cached_result:
                        # Use cached results
                        file_result = cached_result
                        file_result['cache_hit'] = True
                    else:
                        # Read file content
                        try:
                            with open(file_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                                file_content = f.read()
                        except Exception as e:
                            print(f"⚠️ Failed to read file {file_info.relative_path}: {e}")
                            continue
                        
                        # Run security analysis on file
                        file_result = await security_agent.run(
                            code=file_content,
                            language=file_info.language,
                            filename=file_info.relative_path,
                            use_advanced_analysis=use_advanced_analysis
                        )
                        
                        file_result['cache_hit'] = False
                        
                        # Cache the results
                        if cache_enabled:
                            await cache_service.cache_scan_results(
                                file_info.content_hash,
                                file_info.language,
                                {'use_advanced_analysis': use_advanced_analysis},
                                file_result
                            )
                    
                    # Store file-specific results
                    file_results[file_info.relative_path] = {
                        'file_info': asdict(file_info),
                        'scan_results': file_result,
                        'vulnerabilities_count': len(file_result.get('vulnerabilities', [])),
                        'patches_count': len(file_result.get('patches', []))
                    }
                    
                    # Aggregate results
                    file_vulnerabilities = file_result.get('vulnerabilities', [])
                    file_patches = file_result.get('patches', [])
                    
                    # Add file context to vulnerabilities
                    for vuln in file_vulnerabilities:
                        vuln['file_path'] = file_info.relative_path
                        vuln['file_size'] = file_info.size
                        vuln['language'] = file_info.language
                    
                    # Add file context to patches
                    for patch in file_patches:
                        if 'vuln' in patch and isinstance(patch['vuln'], dict):
                            patch['vuln']['file_path'] = file_info.relative_path
                    
                    all_vulnerabilities.extend(file_vulnerabilities)
                    all_patches.extend(file_patches)
                    
                except Exception as e:
                    print(f"⚠️ Error processing file {file_info.relative_path}: {e}")
                    # Continue with next file
                    continue
        
        # Progress: Aggregating results
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'aggregating',
            'progress': 85,
            'message': 'Aggregating scan results...'
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'processing',
            'stage': 'aggregating',
            'progress': 85,
            'message': 'Aggregating scan results...'
        })
        
        # Create aggregated results
        aggregated_results = _create_aggregated_results(
            all_vulnerabilities, all_patches, file_results, repo_metadata, discovered_files
        )
        
        # Progress: Finalizing
        await cache_service.set_job_progress(job_id, {
            'status': 'processing',
            'stage': 'finalizing',
            'progress': 95,
            'message': 'Finalizing repository scan...'
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'processing',
            'stage': 'finalizing',
            'progress': 95,
            'message': 'Finalizing repository scan...'
        })
        
        # Calculate execution time
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - start_time).total_seconds()
        
        # Final progress update
        await cache_service.set_job_progress(job_id, {
            'status': 'completed',
            'stage': 'completed',
            'progress': 100,
            'message': f'Repository scan completed in {execution_time:.1f}s',
            'completed_at': end_time.isoformat(),
            'execution_time': execution_time,
            'total_files': len(discovered_files),
            'files_processed': files_processed,
            'total_vulnerabilities': len(all_vulnerabilities),
            'total_patches': len(all_patches)
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'completed',
            'stage': 'completed', 
            'progress': 100,
            'message': f'Repository scan completed in {execution_time:.1f}s',
            'completed_at': end_time.isoformat(),
            'execution_time': execution_time,
            'total_files': len(discovered_files),
            'files_processed': files_processed,
            'total_vulnerabilities': len(all_vulnerabilities),
            'total_patches': len(all_patches)
        })
        
        return {
            'job_id': job_id,
            'status': 'completed',
            'results': aggregated_results,
            'metadata': {
                'execution_time': execution_time,
                'started_at': start_time.isoformat(),
                'completed_at': end_time.isoformat(),
                'total_files': len(discovered_files),
                'files_processed': files_processed,
                'total_vulnerabilities': len(all_vulnerabilities),
                'total_patches': len(all_patches),
                'repository_metadata': repo_metadata,
                'scan_configuration': {
                    'repository_url': repository_url,
                    'branch': branch,
                    'commit': commit,
                    'use_advanced_analysis': use_advanced_analysis,
                    'batch_size': batch_size
                }
            }
        }
        
    except Exception as e:
        # Handle errors
        error_time = datetime.now(timezone.utc)
        execution_time = (error_time - start_time).total_seconds()
        
        await cache_service.set_job_progress(job_id, {
            'status': 'failed',
            'stage': 'error',
            'progress': 0,
            'message': f'Repository scan failed: {str(e)}',
            'error': str(e),
            'failed_at': error_time.isoformat(),
            'execution_time': execution_time
        })
        
        await _publish_repo_progress_update(job_id, {
            'status': 'failed',
            'stage': 'error',
            'progress': 0,
            'message': f'Repository scan failed: {str(e)}',
            'error': str(e),
            'failed_at': error_time.isoformat(),
            'execution_time': execution_time
        })
        
        # Re-raise for Celery error handling
        raise Exception(f"Repository scan failed: {str(e)}")
        
    finally:
        # Cleanup cloned repository
        if repo_info:
            git_service.cleanup_repository(repo_info)

def _create_aggregated_results(
    vulnerabilities: List[Dict],
    patches: List[Dict], 
    file_results: Dict[str, Any],
    repo_metadata: Dict[str, Any],
    discovered_files: List[FileInfo]
) -> Dict[str, Any]:
    """Create aggregated repository scan results"""
    
    # Vulnerability statistics
    severity_counts = {}
    language_stats = {}
    file_stats = {}
    
    for vuln in vulnerabilities:
        # Severity breakdown
        severity = vuln.get('severity', 'UNKNOWN')
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        # Language breakdown
        language = vuln.get('language', 'unknown')
        if language not in language_stats:
            language_stats[language] = {'vulnerabilities': 0, 'files': set()}
        language_stats[language]['vulnerabilities'] += 1
        language_stats[language]['files'].add(vuln.get('file_path', ''))
    
    # Convert sets to counts for JSON serialization
    for lang_stat in language_stats.values():
        lang_stat['affected_files'] = len(lang_stat['files'])
        del lang_stat['files']
    
    # File statistics
    files_with_vulnerabilities = set()
    for vuln in vulnerabilities:
        file_path = vuln.get('file_path')
        if file_path:
            files_with_vulnerabilities.add(file_path)
    
    # Top vulnerability types
    vulnerability_types = {}
    for vuln in vulnerabilities:
        vuln_type = vuln.get('title', 'Unknown')
        vulnerability_types[vuln_type] = vulnerability_types.get(vuln_type, 0) + 1
    
    top_vulnerability_types = sorted(
        vulnerability_types.items(), 
        key=lambda x: x[1], 
        reverse=True
    )[:10]
    
    return {
        'repository_info': repo_metadata,
        'scan_summary': {
            'total_files_discovered': len(discovered_files),
            'total_files_scanned': len(file_results),
            'total_vulnerabilities': len(vulnerabilities),
            'total_patches_generated': len(patches),
            'files_with_vulnerabilities': len(files_with_vulnerabilities),
            'clean_files': len(file_results) - len(files_with_vulnerabilities)
        },
        'vulnerability_breakdown': {
            'by_severity': severity_counts,
            'by_language': language_stats,
            'by_type': dict(top_vulnerability_types)
        },
        'file_results': file_results,
        'all_vulnerabilities': vulnerabilities,
        'all_patches': patches,
        'languages_detected': list(set(f.language for f in discovered_files)),
        'file_extensions_scanned': list(set(Path(f.path).suffix for f in discovered_files))
    }