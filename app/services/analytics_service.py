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
        """Get complete dashboard overview"""
        try:
            # Get all the component data
            metrics = await self.get_security_metrics(time_range)
            trends = await self.get_vulnerability_trends(time_range)
            repositories = await self.get_repository_stats(limit=10)
            performance = await self.get_performance_metrics()
            
            return DashboardOverview(
                metrics=metrics,
                trends=trends,
                top_repositories=repositories,
                performance=performance,
                time_range=time_range
            )
            
        except Exception as e:
            print(f"❌ Error getting dashboard overview: {e}")
            # Return empty dashboard instead of failing
            return DashboardOverview(
                metrics=SecurityMetrics(),
                time_range=time_range
            )

    async def get_security_metrics(self, time_range: TimeRange) -> SecurityMetrics:
        """Get aggregated security metrics"""
        try:
            session = self.get_db_session()
            
            # Calculate time window
            end_time = datetime.now(timezone.utc)
            start_time = self._get_start_time(end_time, time_range)
            
            # Query scans in time range
            scans = session.query(ScanRecord).filter(
                and_(
                    ScanRecord.timestamp >= start_time,
                    ScanRecord.timestamp <= end_time
                )
            ).all()
            
            # Calculate metrics
            total_scans = len(scans)
            total_files = sum(scan.files_scanned or 1 for scan in scans)
            unique_repos = len(set(scan.repo_url for scan in scans if scan.repo_url))
            
            # Vulnerability distribution
            vuln_dist = VulnerabilityDistribution()
            total_scan_duration = 0
            valid_durations = 0
            
            for scan in scans:
                vuln_dist.critical += scan.critical_count or 0
                vuln_dist.high += scan.high_count or 0
                vuln_dist.medium += scan.medium_count or 0
                vuln_dist.low += scan.low_count or 0
                
                if scan.scan_duration:
                    total_scan_duration += scan.scan_duration
                    valid_durations += 1
            
            vuln_dist.calculate_total()
            
            # Calculate overall security score (weighted average)
            if scans:
                avg_security_score = sum(scan.security_score or 0 for scan in scans) / len(scans)
                avg_scan_duration = total_scan_duration / valid_durations if valid_durations > 0 else 0
            else:
                avg_security_score = 100.0
                avg_scan_duration = 0.0
            
            # Get top vulnerability types
            top_vuln_types = session.query(
                RuleHitRecord.rule_name,
                RuleHitRecord.severity,
                func.sum(RuleHitRecord.hit_count).label('total_hits')
            ).filter(
                RuleHitRecord.scan_id.in_([scan.id for scan in scans])
            ).group_by(
                RuleHitRecord.rule_name, RuleHitRecord.severity
            ).order_by(
                desc('total_hits')
            ).limit(5).all()
            
            top_vulnerability_types = [
                {
                    "rule_name": rule_name,
                    "severity": severity,
                    "count": int(total_hits)
                }
                for rule_name, severity, total_hits in top_vuln_types
            ]
            
            session.close()
            
            return SecurityMetrics(
                total_scans=total_scans,
                total_files=total_files,
                total_repositories=unique_repos,
                vulnerability_distribution=vuln_dist,
                security_score=round(avg_security_score, 1),
                avg_scan_duration=round(avg_scan_duration, 2),
                cache_hit_rate=0.0,  # TODO: implement cache metrics
                scan_success_rate=100.0,  # TODO: track failures
                top_vulnerability_types=top_vulnerability_types,
                recent_activity={}  # TODO: implement recent activity
            )
            
        except Exception as e:
            print(f"❌ Error getting security metrics: {e}")
            return SecurityMetrics()
    async def get_vulnerability_trends(self, time_range: TimeRange) -> List[VulnerabilityTrend]:
        """Get vulnerability trends over time"""
        try:
            session = self.get_db_session()
            
            end_time = datetime.now(timezone.utc)
            start_time = self._get_start_time(end_time, time_range)
            
            # Query scans in time range
            scans = session.query(ScanRecord).filter(
                and_(
                    ScanRecord.timestamp >= start_time,
                    ScanRecord.timestamp <= end_time
                )
            ).order_by(ScanRecord.timestamp).all()
            
            # Group by time buckets and severity
            trends = []
            severity_levels = ["low", "medium", "high", "critical"]
            
            # Create time buckets
            time_buckets = self._create_time_buckets(start_time, end_time, time_range)
            
            for bucket_start, bucket_end in time_buckets:
                bucket_scans = [
                    scan for scan in scans 
                    if bucket_start <= scan.timestamp < bucket_end
                ]
                
                for severity in severity_levels:
                    count = 0
                    repo = None
                    
                    for scan in bucket_scans:
                        if severity == "critical":
                            count += scan.critical_count or 0
                        elif severity == "high":
                            count += scan.high_count or 0
                        elif severity == "medium":
                            count += scan.medium_count or 0
                        elif severity == "low":
                            count += scan.low_count or 0
                        
                        if not repo and scan.repo_url:
                            repo = scan.repo_url
                    
                    if count > 0 or len(bucket_scans) > 0:  # Include zero points for continuity
                        trends.append(VulnerabilityTrend(
                            timestamp=bucket_start,
                            count=count,
                            severity=SeverityLevel(severity),
                            repository=repo
                        ))
            
            session.close()
            return trends
            
        except Exception as e:
            print(f"❌ Error getting vulnerability trends: {e}")
            return []
    
    async def get_repository_stats(self, limit: int = 20) -> List[RepositoryStats]:
        """Get repository statistics"""
        try:
            session = self.get_db_session()
            
            # Get repositories with their latest stats
            repo_stats = session.query(
                ScanRecord.repo_url,
                ScanRecord.repository_name,
                ScanRecord.branch,
                func.count(ScanRecord.id).label('total_scans'),
                func.sum(ScanRecord.files_scanned).label('total_files'),
                func.avg(ScanRecord.security_score).label('avg_security_score'),
                func.sum(ScanRecord.critical_count).label('total_critical'),
                func.sum(ScanRecord.high_count).label('total_high'),
                func.sum(ScanRecord.medium_count).label('total_medium'),
                func.sum(ScanRecord.low_count).label('total_low'),
                func.max(ScanRecord.timestamp).label('last_scan'),
                func.avg(ScanRecord.scan_duration).label('avg_duration')
            ).filter(
                ScanRecord.repo_url.isnot(None)
            ).group_by(
                ScanRecord.repo_url, ScanRecord.repository_name, ScanRecord.branch
            ).order_by(
                desc('avg_security_score')
            ).limit(limit).all()
            
            repositories = []
            for stat in repo_stats:
                vuln_dist = VulnerabilityDistribution(
                    critical=int(stat.total_critical or 0),
                    high=int(stat.total_high or 0),
                    medium=int(stat.total_medium or 0),
                    low=int(stat.total_low or 0)
                )
                vuln_dist.calculate_total()
                
                repositories.append(RepositoryStats(
                    repository_url=stat.repo_url,
                    repository_name=stat.repository_name or stat.repo_url.split('/')[-1],
                    branch=stat.branch or "main",
                    security_score=round(float(stat.avg_security_score or 0), 1),
                    total_vulnerabilities=vuln_dist.total,
                    vulnerability_distribution=vuln_dist,
                    total_scans=int(stat.total_scans),
                    total_files=int(stat.total_files or 0),
                    last_scan_date=stat.last_scan,
                    languages=[],  # TODO: extract from metadata
                    avg_scan_duration=round(float(stat.avg_duration or 0), 2)
                ))
            
            session.close()
            return repositories
            
        except Exception as e:
            print(f"❌ Error getting repository stats: {e}")
            return []
    
    async def get_performance_metrics(self) -> List[ScanPerformanceMetrics]:
        """Get scan performance metrics"""
        try:
            session = self.get_db_session()
            
            # Group by scan type
            performance_stats = session.query(
                ScanRecord.scan_type,
                func.count(ScanRecord.id).label('total_scans'),
                func.avg(ScanRecord.scan_duration).label('avg_duration'),
                func.min(ScanRecord.scan_duration).label('min_duration'),
                func.max(ScanRecord.scan_duration).label('max_duration')
            ).filter(
                ScanRecord.scan_duration.isnot(None)
            ).group_by(
                ScanRecord.scan_type
            ).all()
            
            performance = []
            for stat in performance_stats:
                performance.append(ScanPerformanceMetrics(
                    scan_type=stat.scan_type,
                    avg_duration=round(float(stat.avg_duration or 0), 2),
                    min_duration=round(float(stat.min_duration or 0), 2),
                    max_duration=round(float(stat.max_duration or 0), 2),
                    success_rate=100.0,  # TODO: track failures
                    total_scans=int(stat.total_scans),
                    cache_hit_rate=0.0  # TODO: implement
                ))
            
            session.close()
            return performance
            
        except Exception as e:
            print(f"❌ Error getting performance metrics: {e}")
            return []
    
    # CLI-specific methods for new commands
    
    async def get_scan_summary(self, scan_id: Optional[str] = None) -> Optional[ScanSummary]:
        """Get summary for specific scan or latest scan"""
        try:
            session = self.get_db_session()
            
            if scan_id:
                scan = session.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
            else:
                scan = session.query(ScanRecord).order_by(desc(ScanRecord.timestamp)).first()
            
            if not scan:
                session.close()
                return None
            
            # Get top rule hits for this scan
            top_rules = session.query(
                RuleHitRecord.rule_name,
                RuleHitRecord.severity,
                func.sum(RuleHitRecord.hit_count).label('total_hits')
            ).filter(
                RuleHitRecord.scan_id == scan.id
            ).group_by(
                RuleHitRecord.rule_name, RuleHitRecord.severity
            ).order_by(
                desc('total_hits')
            ).limit(5).all()
            
            top_rules_list = [
                {
                    "rule_name": rule_name,
                    "severity": severity,
                    "hits": int(total_hits)
                }
                for rule_name, severity, total_hits in top_rules
            ]
            
            session.close()
            
            return ScanSummary(
                scan_id=scan.id,
                timestamp=scan.timestamp,
                repository=scan.repo_url,
                total_issues=scan.total_issues or 0,
                critical_count=scan.critical_count or 0,
                high_count=scan.high_count or 0,
                medium_count=scan.medium_count or 0,
                low_count=scan.low_count or 0,
                security_score=scan.security_score or 0.0,
                scan_duration=scan.scan_duration,
                files_scanned=scan.files_scanned or 0,
                top_rules=top_rules_list,
                languages=[scan.language] if scan.language else []
            )
            
        except Exception as e:
            print(f"❌ Error getting scan summary: {e}")
            return None
    
    async def get_trend_data(self, days: int = 30) -> List[TrendDataPoint]:
        """Get trend data for CLI visualization"""
        try:
            session = self.get_db_session()
            
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(days=days)
            
            # Group by day
            daily_stats = session.query(
                func.date(ScanRecord.timestamp).label('scan_date'),
                func.count(ScanRecord.id).label('total_scans'),
                func.sum(ScanRecord.total_issues).label('total_vulnerabilities'),
                func.sum(ScanRecord.critical_count).label('critical'),
                func.sum(ScanRecord.high_count).label('high'),
                func.sum(ScanRecord.medium_count).label('medium'),
                func.sum(ScanRecord.low_count).label('low')
            ).filter(
                and_(
                    ScanRecord.timestamp >= start_time,
                    ScanRecord.timestamp <= end_time
                )
            ).group_by(
                func.date(ScanRecord.timestamp)
            ).order_by('scan_date').all()
            
            trends = []
            for stat in daily_stats:
                trends.append(TrendDataPoint(
                    date=str(stat.scan_date),
                    total_scans=int(stat.total_scans or 0),
                    total_vulnerabilities=int(stat.total_vulnerabilities or 0),
                    critical=int(stat.critical or 0),
                    high=int(stat.high or 0),
                    medium=int(stat.medium or 0),
                    low=int(stat.low or 0)
                ))
            
            session.close()
            return trends
            
        except Exception as e:
            print(f"❌ Error getting trend data: {e}")
            return []
    
    async def get_heatmap_data(self, scan_id: Optional[str] = None) -> List[HeatmapEntry]:
        """Get heatmap data for directory visualization"""
        try:
            session = self.get_db_session()
            
            # Get latest scan if no ID provided
            if not scan_id:
                latest_scan = session.query(ScanRecord).order_by(desc(ScanRecord.timestamp)).first()
                if not latest_scan:
                    return []
                scan_id = latest_scan.id
            
            # Get rule hits grouped by file path
            rule_hits = session.query(
                RuleHitRecord.file_path,
                func.sum(RuleHitRecord.hit_count).label('total_hits'),
                func.count(RuleHitRecord.id).label('rule_count')
            ).filter(
                and_(
                    RuleHitRecord.scan_id == scan_id,
                    RuleHitRecord.file_path.isnot(None)
                )
            ).group_by(
                RuleHitRecord.file_path
            ).all()
            
            # Convert to directory-level heatmap
            dir_stats = {}
            for hit in rule_hits:
                file_path = hit.file_path
                if file_path:
                    # Extract directory
                    dir_path = str(Path(file_path).parent)
                    if dir_path not in dir_stats:
                        dir_stats[dir_path] = {
                            "hits": 0,
                            "files": set(),
                            "severity_score": 0
                        }
                    dir_stats[dir_path]["hits"] += int(hit.total_hits)
                    dir_stats[dir_path]["files"].add(file_path)
            
            heatmap = []
            for dir_path, stats in dir_stats.items():
                heatmap.append(HeatmapEntry(
                    path=dir_path,
                    rule_hits=stats["hits"],
                    severity_score=float(stats["hits"]),  # Simple scoring for now
                    files_count=len(stats["files"])
                ))
            
            # Sort by rule hits descending
            heatmap.sort(key=lambda x: x.rule_hits, reverse=True)
            
            session.close()
            return heatmap
            
        except Exception as e:
            print(f"❌ Error getting heatmap data: {e}")
            return []
    
    async def get_scan_history(self, limit: int = 20, **filters) -> List[ScanHistoryEntry]:
        """Get scan history for CLI with advanced filtering"""
        try:
            session = self.get_db_session()
            
            # Base query
            query = session.query(ScanRecord)
            
            # Apply filters
            if filters.get('since'):
                query = query.filter(ScanRecord.timestamp >= filters['since'])
            
            if filters.get('until'):
                query = query.filter(ScanRecord.timestamp <= filters['until'])
                
            if filters.get('min_score') is not None:
                query = query.filter(ScanRecord.security_score >= filters['min_score'])
                
            if filters.get('max_score') is not None:
                query = query.filter(ScanRecord.security_score <= filters['max_score'])
                
            if filters.get('repo'):
                query = query.filter(ScanRecord.repo_url.contains(filters['repo']))
                
            if filters.get('language'):
                query = query.filter(ScanRecord.language == filters['language'])
                
            if filters.get('scan_type'):
                query = query.filter(ScanRecord.scan_type == filters['scan_type'])
            
            # Order by timestamp descending and apply limit
            scans = query.order_by(desc(ScanRecord.timestamp)).limit(limit).all()
            
            history = []
            for scan in scans:
                # Get top 3 issue types
                top_issues = session.query(
                    RuleHitRecord.rule_name
                ).filter(
                    RuleHitRecord.scan_id == scan.id
                ).group_by(
                    RuleHitRecord.rule_name
                ).order_by(
                    desc(func.sum(RuleHitRecord.hit_count))
                ).limit(3).all()
                
                top_issues_list = [issue.rule_name for issue in top_issues]
                
                history.append(ScanHistoryEntry(
                    scan_id=scan.id,
                    timestamp=scan.timestamp,
                    repository=scan.repo_url,
                    total_issues=scan.total_issues or 0,
                    security_score=scan.security_score or 0.0,
                    top_issues=top_issues_list,
                    scan_type=scan.scan_type or "single_file",
                    duration=scan.scan_duration
                ))
            
            session.close()
            return history
            
        except Exception as e:
            print(f"❌ Error getting scan history: {e}")
            return []
    
    async def get_scan_summary_filtered(self, scan_id: Optional[str] = None, **filters) -> Optional[ScanSummary]:
        """Get filtered scan summary with rule and severity filtering"""
        try:
            session = self.get_db_session()
            
            if scan_id:
                scan = session.query(ScanRecord).filter(ScanRecord.id == scan_id).first()
            else:
                scan = session.query(ScanRecord).order_by(desc(ScanRecord.timestamp)).first()
            
            if not scan:
                session.close()
                return None
            
            # Base query for rule hits
            rule_query = session.query(
                RuleHitRecord.rule_name,
                RuleHitRecord.severity,
                func.sum(RuleHitRecord.hit_count).label('total_hits')
            ).filter(
                RuleHitRecord.scan_id == scan.id
            )
            
            # Apply filters
            if filters.get('rule'):
                rule_query = rule_query.filter(RuleHitRecord.rule_name.contains(filters['rule']))
                
            if filters.get('severity'):
                rule_query = rule_query.filter(RuleHitRecord.severity == filters['severity'])
            
            top_rules = rule_query.group_by(
                RuleHitRecord.rule_name, RuleHitRecord.severity
            ).order_by(
                desc('total_hits')
            ).limit(10).all()
            
            top_rules_list = [
                {
                    "rule_name": rule_name,
                    "severity": severity,
                    "hits": int(total_hits)
                }
                for rule_name, severity, total_hits in top_rules
            ]
            
            # Recalculate counts if filtering applied
            if filters.get('severity'):
                # Get filtered counts
                filtered_counts = {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0
                }
                if filters['severity'] in filtered_counts:
                    if filters['severity'] == 'critical':
                        filtered_counts['critical'] = scan.critical_count or 0
                    elif filters['severity'] == 'high':
                        filtered_counts['high'] = scan.high_count or 0
                    elif filters['severity'] == 'medium':
                        filtered_counts['medium'] = scan.medium_count or 0
                    elif filters['severity'] == 'low':
                        filtered_counts['low'] = scan.low_count or 0
                
                total_filtered = sum(filtered_counts.values())
            else:
                filtered_counts = {
                    'critical': scan.critical_count or 0,
                    'high': scan.high_count or 0,
                    'medium': scan.medium_count or 0,
                    'low': scan.low_count or 0
                }
                total_filtered = scan.total_issues or 0
            
            session.close()
            
            return ScanSummary(
                scan_id=scan.id,
                timestamp=scan.timestamp,
                repository=scan.repo_url,
                total_issues=total_filtered,
                critical_count=filtered_counts['critical'],
                high_count=filtered_counts['high'],
                medium_count=filtered_counts['medium'],
                low_count=filtered_counts['low'],
                security_score=scan.security_score or 0.0,
                scan_duration=scan.scan_duration,
                files_scanned=scan.files_scanned or 0,
                top_rules=top_rules_list,
                languages=[scan.language] if scan.language else []
            )
            
        except Exception as e:
            print(f"❌ Error getting filtered scan summary: {e}")
            return None

    async def get_repository_stats_filtered(self, limit: int = 20, **filters) -> List[RepositoryStats]:
        """Get repository statistics with filtering"""
        try:
            session = self.get_db_session()
            
            # Base query
            query = session.query(
                ScanRecord.repo_url,
                ScanRecord.repository_name,
                ScanRecord.branch,
                func.count(ScanRecord.id).label('total_scans'),
                func.sum(ScanRecord.files_scanned).label('total_files'),
                func.avg(ScanRecord.security_score).label('avg_security_score'),
                func.sum(ScanRecord.critical_count).label('total_critical'),
                func.sum(ScanRecord.high_count).label('total_high'),
                func.sum(ScanRecord.medium_count).label('total_medium'),
                func.sum(ScanRecord.low_count).label('total_low'),
                func.max(ScanRecord.timestamp).label('last_scan'),
                func.avg(ScanRecord.scan_duration).label('avg_duration')
            ).filter(
                ScanRecord.repo_url.isnot(None)
            )
            
            # Apply filters
            if filters.get('min_score') is not None:
                query = query.having(func.avg(ScanRecord.security_score) >= filters['min_score'])
                
            if filters.get('language'):
                query = query.filter(ScanRecord.language == filters['language'])
                
            if filters.get('since'):
                query = query.filter(ScanRecord.timestamp >= filters['since'])
            
            repo_stats = query.group_by(
                ScanRecord.repo_url, ScanRecord.repository_name, ScanRecord.branch
            ).order_by(
                desc('avg_security_score')
            ).limit(limit).all()
            
            repositories = []
            for stat in repo_stats:
                vuln_dist = VulnerabilityDistribution(
                    critical=int(stat.total_critical or 0),
                    high=int(stat.total_high or 0),
                    medium=int(stat.total_medium or 0),
                    low=int(stat.total_low or 0)
                )
                vuln_dist.calculate_total()
                
                repositories.append(RepositoryStats(
                    repository_url=stat.repo_url,
                    repository_name=stat.repository_name or stat.repo_url.split('/')[-1],
                    branch=stat.branch or "main",
                    security_score=round(float(stat.avg_security_score or 0), 1),
                    total_vulnerabilities=vuln_dist.total,
                    vulnerability_distribution=vuln_dist,
                    total_scans=int(stat.total_scans),
                    total_files=int(stat.total_files or 0),
                    last_scan_date=stat.last_scan,
                    languages=[],  # TODO: extract from metadata
                    avg_scan_duration=round(float(stat.avg_duration or 0), 2)
                ))
            
            session.close()
            return repositories
            
        except Exception as e:
            print(f"❌ Error getting filtered repository stats: {e}")
            return []
    
    # Helper methods
    
    def _get_start_time(self, end_time: datetime, time_range: TimeRange) -> datetime:
        """Calculate start time based on time range"""
        if time_range == TimeRange.LAST_HOUR:
            return end_time - timedelta(hours=1)
        elif time_range == TimeRange.LAST_DAY:
            return end_time - timedelta(days=1)
        elif time_range == TimeRange.LAST_WEEK:
            return end_time - timedelta(days=7)
        elif time_range == TimeRange.LAST_MONTH:
            return end_time - timedelta(days=30)
        elif time_range == TimeRange.LAST_QUARTER:
            return end_time - timedelta(days=90)
        elif time_range == TimeRange.LAST_YEAR:
            return end_time - timedelta(days=365)
        else:
            return end_time - timedelta(days=1)  # Default to last day
    
    def _create_time_buckets(self, start_time: datetime, end_time: datetime, time_range: TimeRange):
        """Create time buckets for trend analysis"""
        buckets = []
        
        # Determine bucket size
        if time_range in [TimeRange.LAST_HOUR]:
            delta = timedelta(minutes=5)  # 5-minute buckets
        elif time_range in [TimeRange.LAST_DAY]:
            delta = timedelta(hours=1)    # Hourly buckets
        elif time_range in [TimeRange.LAST_WEEK]:
            delta = timedelta(hours=6)    # 6-hour buckets
        else:
            delta = timedelta(days=1)     # Daily buckets
        
        current_time = start_time
        while current_time < end_time:
            bucket_end = min(current_time + delta, end_time)
            buckets.append((current_time, bucket_end))
            current_time = bucket_end
        
        return buckets


# Global analytics service instance
analytics_service = AnalyticsService()