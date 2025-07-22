"""
Analytics Service for Phase 7: CLI Monitoring & Analytics
Handles database operations, data aggregation, and metrics calculation with SQLite storage
"""
import asyncio
import json
import sqlite3
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from collections import defaultdict
import redis.asyncio as redis
from sqlalchemy import create_engine, desc, func, and_
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.services.cache_service import cache_service
from app.models.analytics import (
    Base, ScanRecord, RuleHitRecord,
    DashboardOverview, SecurityMetrics, VulnerabilityTrend, RepositoryStats,
    VulnerabilityDistribution, ScanPerformanceMetrics, TimeRange, SeverityLevel,
    ScanSummary, TrendDataPoint, HeatmapEntry, ScanHistoryEntry, ScanType,
    TimeSeries, MetricsCalculator
)


class AnalyticsService:
    """Service for analytics data management and aggregation with SQLite storage"""
    
    def __init__(self, database_url: str = "sqlite:///./analytics.db"):
        self.database_url = database_url
        self.engine = None
        self.SessionLocal = None
        self.redis_client = None
        self.metrics_calculator = MetricsCalculator()
        
    async def connect(self):
        """Initialize database connection and create tables"""
        try:
            # Create SQLAlchemy engine and session
            self.engine = create_engine(
                self.database_url,
                connect_args={"check_same_thread": False} if "sqlite" in self.database_url else {}
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Connect to Redis for caching (optional)
            try:
                if not cache_service.connected:
                    await cache_service.connect()
                self.redis_client = cache_service.redis_client
                print("✅ Analytics service connected to Redis cache")
            except Exception as e:
                print(f"⚠️ Analytics service: Redis unavailable, using database only: {e}")
                self.redis_client = None
            
            print("✅ Analytics service initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize analytics service: {e}")
            raise
    
    def get_db_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    # Core data storage methods
    
    async def store_scan_result(
        self, 
        scan_id: str,
        scan_results: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store scan results in the database
        Called after each completed scan
        """
        try:
            session = self.get_db_session()
            
            # Extract data from scan results
            vulnerabilities = scan_results.get("vulnerabilities", [])
            repo_url = metadata.get("repository_url") if metadata else None
            repository_name = metadata.get("repository_name") if metadata else None
            branch = metadata.get("branch") if metadata else None
            scan_duration = metadata.get("execution_time") if metadata else None
            language = metadata.get("language") if metadata else None
            model_used = metadata.get("model") if metadata else None
            scan_type = metadata.get("scan_type", "single_file") if metadata else "single_file"
            files_scanned = metadata.get("files_scanned", 1) if metadata else 1
            
            # Count vulnerabilities by severity
            severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for vuln in vulnerabilities:
                severity = vuln.get("severity", "low").lower()
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            total_issues = len(vulnerabilities)
            
            # Calculate security score (simple algorithm: 100 - weighted severity score)
            security_score = max(0, 100 - (
                severity_counts["critical"] * 25 +
                severity_counts["high"] * 10 +
                severity_counts["medium"] * 5 +
                severity_counts["low"] * 1
            ))
            
            # Create scan record
            scan_record = ScanRecord(
                id=scan_id,
                repo_url=repo_url,
                repository_name=repository_name,
                branch=branch,
                timestamp=datetime.now(timezone.utc),
                total_issues=total_issues,
                critical_count=severity_counts["critical"],
                high_count=severity_counts["high"],
                medium_count=severity_counts["medium"], 
                low_count=severity_counts["low"],
                files_scanned=files_scanned,
                scan_duration=scan_duration,
                security_score=security_score,
                language=language,
                model_used=model_used,
                scan_type=scan_type,
                scan_metadata=json.dumps(metadata) if metadata else None
            )
            
            session.add(scan_record)
            
            # Store rule hits
            rule_hit_counts = {}
            for vuln in vulnerabilities:
                rule_name = vuln.get("id", "unknown")
                rule_id = vuln.get("title", rule_name)
                severity = vuln.get("severity", "low").lower()
                tool = vuln.get("tool", "unknown")
                file_path = metadata.get("file_path") if metadata else None
                line_number = vuln.get("line_number")
                
                # Count hits per rule
                rule_key = f"{rule_name}:{severity}:{tool}"
                if rule_key not in rule_hit_counts:
                    rule_hit_counts[rule_key] = {
                        "rule_name": rule_name,
                        "rule_id": rule_id,
                        "severity": severity,
                        "tool": tool,
                        "count": 0,
                        "file_path": file_path,
                        "line_number": line_number
                    }
                rule_hit_counts[rule_key]["count"] += 1
            
            # Store rule hit records
            for rule_data in rule_hit_counts.values():
                rule_hit = RuleHitRecord(
                    scan_id=scan_id,
                    rule_name=rule_data["rule_name"],
                    rule_id=rule_data["rule_id"], 
                    hit_count=rule_data["count"],
                    severity=rule_data["severity"],
                    tool=rule_data["tool"],
                    file_path=rule_data["file_path"],
                    line_number=rule_data["line_number"]
                )
                session.add(rule_hit)
            
            session.commit()
            session.close()
            
            return scan_id
            
        except Exception as e:
            print(f"❌ Error storing scan result: {e}")
            if session:
                session.rollback()
                session.close()
            raise

    async def get_dashboard_overview(self, time_range: TimeRange) -> DashboardOverview:
        """Get complete dashboard overview data"""
        
        try:
            # Check cache first
            cache_key = f"{self.cache_prefix}overview:{time_range.value}"
            cached_data = await self.redis_client.get(cache_key)
            
            if cached_data:
                data = json.loads(cached_data)
                # Convert datetime strings back to datetime objects
                return self._deserialize_dashboard_overview(data)
            
            # Calculate fresh metrics
            overview = await self._calculate_dashboard_overview(time_range)
            
            # Cache for 5 minutes
            await self.redis_client.setex(
                cache_key,
                300,
                json.dumps(overview.model_dump(), default=str)
            )
            
            return overview
            
        except Exception as e:
            print(f"❌ Error getting dashboard overview: {e}")
            return self._get_empty_dashboard_overview(time_range)
    
    async def get_security_metrics(
        self, 
        time_range: TimeRange = TimeRange.LAST_DAY
    ) -> SecurityMetrics:
        """Get aggregated security metrics"""
        
        try:
            end_time = datetime.now(timezone.utc)
            start_time = self._get_start_time(end_time, time_range)
            
            # Get all job keys in time range
            job_keys = await self.redis_client.keys("job:*")
            
            total_scans = 0
            total_files = 0
            total_repos = 0
            vulnerability_counts = defaultdict(int)
            scan_times = []
            cache_hits = 0
            recent_scans = 0
            recent_vulns = 0
            
            # Analyze each scan
            for job_key in job_keys:
                job_data = await self.redis_client.get(job_key)
                if not job_data:
                    continue
                    
                try:
                    job = json.loads(job_data)
                    
                    # Parse job timestamp
                    job_time = datetime.fromisoformat(
                        job.get('started_at', '').replace('Z', '+00:00')
                    ) if job.get('started_at') else None
                    
                    if not job_time or job_time < start_time:
                        continue
                    
                    # Count scans
                    total_scans += 1
                    
                    # Repository vs single file scans
                    if 'repository_url' in job.get('message', ''):
                        total_repos += 1
                        total_files += job.get('total_files', 0)
                    else:
                        total_files += 1
                    
                    # Scan performance
                    if job.get('execution_time'):
                        scan_times.append(job['execution_time'])
                    
                    if job.get('cache_hit'):
                        cache_hits += 1
                    
                    # Recent activity (last 24 hours)
                    if job_time > end_time - timedelta(hours=24):
                        recent_scans += 1
                        recent_vulns += job.get('total_vulnerabilities', 0)
                    
                    # Count vulnerabilities by severity
                    total_vulns = job.get('total_vulnerabilities', 0)
                    if total_vulns > 0:
                        # Estimate severity distribution (would be better with actual data)
                        vulnerability_counts['CRITICAL'] += max(1, total_vulns // 20)
                        vulnerability_counts['HIGH'] += max(1, total_vulns // 10) 
                        vulnerability_counts['MEDIUM'] += max(1, total_vulns // 5)
                        vulnerability_counts['LOW'] += total_vulns // 2
                        
                except (json.JSONDecodeError, ValueError) as e:
                    continue
            
            # Calculate derived metrics
            avg_scan_time = sum(scan_times) / len(scan_times) if scan_times else 0.0
            cache_hit_rate = (cache_hits / total_scans * 100) if total_scans > 0 else 0.0
            
            total_vulnerabilities = sum(vulnerability_counts.values())
            security_score = self.metrics_calculator.calculate_security_score(
                vulnerability_counts, total_files
            )
            
            return SecurityMetrics(
                total_scans=total_scans,
                total_files_scanned=total_files,
                total_repositories_scanned=total_repos,
                total_vulnerabilities=total_vulnerabilities,
                critical_count=vulnerability_counts.get('CRITICAL', 0),
                high_count=vulnerability_counts.get('HIGH', 0),
                medium_count=vulnerability_counts.get('MEDIUM', 0),
                low_count=vulnerability_counts.get('LOW', 0),
                info_count=vulnerability_counts.get('INFO', 0),
                avg_scan_time=round(avg_scan_time, 2),
                cache_hit_rate=round(cache_hit_rate, 1),
                scans_last_24h=recent_scans,
                new_vulnerabilities_last_24h=recent_vulns,
                security_score=security_score,
                improvement_trend=0.0  # Would need historical comparison
            )
            
        except Exception as e:
            print(f"❌ Error calculating security metrics: {e}")
            return SecurityMetrics()
    
    async def get_vulnerability_trends(
        self, 
        time_range: TimeRange = TimeRange.LAST_WEEK
    ) -> List[VulnerabilityTrend]:
        """Get vulnerability trends over time"""
        
        try:
            end_time = datetime.now(timezone.utc)
            start_time = self._get_start_time(end_time, time_range)
            
            # Get job data in time range
            job_keys = await self.redis_client.keys("job:*")
            trends = []
            
            for job_key in job_keys:
                job_data = await self.redis_client.get(job_key)
                if not job_data:
                    continue
                    
                try:
                    job = json.loads(job_data)
                    
                    job_time = datetime.fromisoformat(
                        job.get('started_at', '').replace('Z', '+00:00')
                    ) if job.get('started_at') else None
                    
                    if not job_time or job_time < start_time:
                        continue
                    
                    # Determine scan type
                    scan_type = ScanType.REPOSITORY if 'repository_url' in job.get('message', '') else ScanType.SINGLE_FILE
                    
                    # Add vulnerability trend points
                    total_vulns = job.get('total_vulnerabilities', 0)
                    if total_vulns > 0:
                        # Simulate severity distribution
                        trends.append(VulnerabilityTrend(
                            timestamp=job_time,
                            severity=SeverityLevel.HIGH,
                            count=max(1, total_vulns // 3),
                            scan_type=scan_type,
                            repository=job.get('repository_url')
                        ))
                        
                        trends.append(VulnerabilityTrend(
                            timestamp=job_time,
                            severity=SeverityLevel.MEDIUM,
                            count=max(1, total_vulns // 2),
                            scan_type=scan_type,
                            repository=job.get('repository_url')
                        ))
                        
                except (json.JSONDecodeError, ValueError):
                    continue
            
            return sorted(trends, key=lambda x: x.timestamp)
            
        except Exception as e:
            print(f"❌ Error getting vulnerability trends: {e}")
            return []
    
    async def get_repository_stats(
        self, 
        limit: int = 20
    ) -> List[RepositoryStats]:
        """Get statistics for top repositories"""
        
        try:
            # Group jobs by repository
            repo_data = defaultdict(lambda: {
                'scans': 0,
                'total_files': 0,
                'vulnerabilities': 0,
                'last_scan': None,
                'scan_times': [],
                'cache_hits': 0
            })
            
            job_keys = await self.redis_client.keys("job:*")
            
            for job_key in job_keys:
                job_data = await self.redis_client.get(job_key)
                if not job_data:
                    continue
                    
                try:
                    job = json.loads(job_data)
                    
                    # Extract repository info
                    message = job.get('message', '')
                    if 'repository_url' not in message:
                        continue  # Skip single file scans
                    
                    # Parse repository URL from message
                    repo_url = message.split(' ')[-1] if message else 'unknown'
                    repo_name = repo_url.split('/')[-1] if '/' in repo_url else repo_url
                    
                    job_time = datetime.fromisoformat(
                        job.get('started_at', '').replace('Z', '+00:00')
                    ) if job.get('started_at') else datetime.now(timezone.utc)
                    
                    # Aggregate repository data
                    data = repo_data[repo_url]
                    data['scans'] += 1
                    data['total_files'] += job.get('total_files', 0)
                    data['vulnerabilities'] += job.get('total_vulnerabilities', 0)
                    
                    if not data['last_scan'] or job_time > data['last_scan']:
                        data['last_scan'] = job_time
                        data['repo_name'] = repo_name
                    
                    if job.get('execution_time'):
                        data['scan_times'].append(job['execution_time'])
                    
                    if job.get('cache_hit'):
                        data['cache_hits'] += 1
                        
                except (json.JSONDecodeError, ValueError):
                    continue
            
            # Convert to RepositoryStats objects
            repo_stats = []
            for repo_url, data in repo_data.items():
                # Calculate security score
                total_files = max(1, data['total_files'])
                security_score = self.metrics_calculator.calculate_security_score(
                    {'HIGH': data['vulnerabilities'] // 3, 'MEDIUM': data['vulnerabilities'] // 2},
                    total_files
                )
                
                # Calculate cache hit rate
                cache_hit_rate = (data['cache_hits'] / data['scans'] * 100) if data['scans'] > 0 else 0.0
                
                # Average scan time
                avg_scan_time = sum(data['scan_times']) / len(data['scan_times']) if data['scan_times'] else None
                
                repo_stats.append(RepositoryStats(
                    repository_url=repo_url,
                    repository_name=data.get('repo_name', repo_url.split('/')[-1]),
                    total_scans=data['scans'],
                    last_scan=data['last_scan'],
                    total_files=data['total_files'],
                    scanned_files=data['total_files'],  # Assume all files were scanned
                    clean_files=max(0, data['total_files'] - data['vulnerabilities']),
                    total_vulnerabilities=data['vulnerabilities'],
                    high_vulnerabilities=data['vulnerabilities'] // 3,
                    medium_vulnerabilities=data['vulnerabilities'] // 2,
                    low_vulnerabilities=data['vulnerabilities'] // 4,
                    security_score=security_score,
                    recent_scan_duration=avg_scan_time,
                    cache_hit_rate=round(cache_hit_rate, 1)
                ))
            
            # Sort by security score (ascending) and total vulnerabilities (descending)
            repo_stats.sort(key=lambda x: (x.security_score, -x.total_vulnerabilities))
            
            return repo_stats[:limit]
            
        except Exception as e:
            print(f"❌ Error getting repository stats: {e}")
            return []
    
    async def get_performance_metrics(self) -> List[ScanPerformanceMetrics]:
        """Get scan performance metrics by type"""
        
        try:
            # Aggregate performance data
            single_file_scans = []
            repo_scans = []
            
            job_keys = await self.redis_client.keys("job:*")
            
            for job_key in job_keys:
                job_data = await self.redis_client.get(job_key)
                if not job_data:
                    continue
                    
                try:
                    job = json.loads(job_data)
                    
                    execution_time = job.get('execution_time', 0)
                    if execution_time <= 0:
                        continue
                    
                    if 'repository_url' in job.get('message', ''):
                        repo_scans.append({
                            'duration': execution_time,
                            'files': job.get('total_files', 0),
                            'success': job.get('status') == 'completed',
                            'cache_hit': job.get('cache_hit', False)
                        })
                    else:
                        single_file_scans.append({
                            'duration': execution_time,
                            'files': 1,
                            'success': job.get('status') == 'completed',
                            'cache_hit': job.get('cache_hit', False)
                        })
                        
                except (json.JSONDecodeError, ValueError):
                    continue
            
            performance_metrics = []
            
            # Single file scan metrics
            if single_file_scans:
                durations = [s['duration'] for s in single_file_scans]
                successes = sum(1 for s in single_file_scans if s['success'])
                cache_hits = sum(1 for s in single_file_scans if s['cache_hit'])
                
                performance_metrics.append(ScanPerformanceMetrics(
                    scan_type=ScanType.SINGLE_FILE,
                    avg_duration=sum(durations) / len(durations),
                    min_duration=min(durations),
                    max_duration=max(durations),
                    total_scans=len(single_file_scans),
                    avg_files_per_scan=1.0,
                    cache_hit_rate=round(cache_hits / len(single_file_scans) * 100, 1),
                    success_rate=round(successes / len(single_file_scans) * 100, 1),
                    failure_rate=round((len(single_file_scans) - successes) / len(single_file_scans) * 100, 1)
                ))
            
            # Repository scan metrics
            if repo_scans:
                durations = [s['duration'] for s in repo_scans]
                files = [s['files'] for s in repo_scans]
                successes = sum(1 for s in repo_scans if s['success'])
                cache_hits = sum(1 for s in repo_scans if s['cache_hit'])
                
                performance_metrics.append(ScanPerformanceMetrics(
                    scan_type=ScanType.REPOSITORY,
                    avg_duration=sum(durations) / len(durations),
                    min_duration=min(durations),
                    max_duration=max(durations),
                    total_scans=len(repo_scans),
                    avg_files_per_scan=sum(files) / len(files) if files else 0,
                    cache_hit_rate=round(cache_hits / len(repo_scans) * 100, 1),
                    success_rate=round(successes / len(repo_scans) * 100, 1),
                    failure_rate=round((len(repo_scans) - successes) / len(repo_scans) * 100, 1)
                ))
            
            return performance_metrics
            
        except Exception as e:
            print(f"❌ Error getting performance metrics: {e}")
            return []
    
    async def _calculate_dashboard_overview(self, time_range: TimeRange) -> DashboardOverview:
        """Calculate complete dashboard overview"""
        
        # Get all components concurrently
        metrics_task = self.get_security_metrics(time_range)
        trends_task = self.get_vulnerability_trends(time_range)
        repos_task = self.get_repository_stats(limit=10)
        performance_task = self.get_performance_metrics()
        
        metrics, trends, repos, performance = await asyncio.gather(
            metrics_task, trends_task, repos_task, performance_task
        )
        
        return DashboardOverview(
            metrics=metrics,
            vulnerability_trends=trends,
            top_repositories=repos,
            performance_metrics=performance,
            time_range=time_range,
            total_data_points=len(trends) + len(repos)
        )
    
    def _get_start_time(self, end_time: datetime, time_range: TimeRange) -> datetime:
        """Get start time for the given time range"""
        range_mapping = {
            TimeRange.LAST_HOUR: timedelta(hours=1),
            TimeRange.LAST_DAY: timedelta(days=1),
            TimeRange.LAST_WEEK: timedelta(weeks=1),
            TimeRange.LAST_MONTH: timedelta(days=30),
            TimeRange.LAST_QUARTER: timedelta(days=90),
            TimeRange.LAST_YEAR: timedelta(days=365)
        }
        
        delta = range_mapping.get(time_range, timedelta(days=1))
        return end_time - delta
    
    def _get_empty_dashboard_overview(self, time_range: TimeRange) -> DashboardOverview:
        """Get empty dashboard overview for error cases"""
        return DashboardOverview(
            metrics=SecurityMetrics(),
            time_range=time_range,
            total_data_points=0
        )
    
    def _deserialize_dashboard_overview(self, data: Dict) -> DashboardOverview:
        """Deserialize dashboard overview from cached JSON data"""
        # Convert datetime strings back to datetime objects
        if data.get('generated_at'):
            data['generated_at'] = datetime.fromisoformat(data['generated_at'].replace('Z', '+00:00'))
        
        return DashboardOverview(**data)

# Global analytics service instance
analytics_service = AnalyticsService()