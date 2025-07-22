"""
Analytics Data Models for Phase 7: CLI Monitoring & Analytics
Pydantic models for dashboard data, scan storage, and analytics responses
"""
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, Integer, String, DateTime, Text, Float, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

# SQLAlchemy Base
Base = declarative_base()

# Enums for API consistency
class TimeRange(str, Enum):
    """Time range options for analytics queries"""
    LAST_HOUR = "1h"
    LAST_DAY = "24h"  
    LAST_WEEK = "7d"
    LAST_MONTH = "30d"
    LAST_QUARTER = "90d"
    LAST_YEAR = "365d"

class SeverityLevel(str, Enum):
    """Vulnerability severity levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    CRITICAL = "critical"

class ScanType(str, Enum):
    """Scan type enumeration"""
    SINGLE_FILE = "single_file"
    REPOSITORY = "repository"
    BULK = "bulk"

class ExportFormat(str, Enum):
    """Export format options"""
    CSV = "csv"
    PDF = "pdf"
    JSON = "json"
    XLSX = "xlsx"

# SQLAlchemy Models for Database Storage

class ScanRecord(Base):
    """SQLAlchemy model for scan metadata storage"""
    __tablename__ = "scans"
    
    id = Column(String, primary_key=True)
    repo_url = Column(String, nullable=True)
    repository_name = Column(String, nullable=True)
    branch = Column(String, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_issues = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    files_scanned = Column(Integer, default=0)
    scan_duration = Column(Float, nullable=True)  # seconds
    security_score = Column(Float, nullable=True)  # 0-100
    language = Column(String, nullable=True)
    model_used = Column(String, nullable=True)
    scan_type = Column(String, default="single_file")  # single_file, repository, bulk
    scan_metadata = Column(Text, nullable=True)  # JSON metadata
    
    # Relationship to rule hits
    rule_hits = relationship("RuleHitRecord", back_populates="scan")

class RuleHitRecord(Base):
    """SQLAlchemy model for rule hit tracking"""
    __tablename__ = "rule_hits"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    scan_id = Column(String, ForeignKey("scans.id"))
    rule_name = Column(String, nullable=False)
    rule_id = Column(String, nullable=True)
    hit_count = Column(Integer, default=1)
    severity = Column(String, nullable=True)
    tool = Column(String, nullable=True)  # bandit, semgrep, custom
    file_path = Column(String, nullable=True)
    line_number = Column(Integer, nullable=True)
    
    # Relationship back to scan
    scan = relationship("ScanRecord", back_populates="rule_hits")

# Pydantic Models for API Responses

class VulnerabilityDistribution(BaseModel):
    """Vulnerability distribution by severity"""
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0
    
    def calculate_total(self):
        self.total = self.critical + self.high + self.medium + self.low

class SecurityMetrics(BaseModel):
    """Core security metrics and KPIs"""
    total_scans: int = 0
    total_files: int = 0
    total_repositories: int = 0
    vulnerability_distribution: VulnerabilityDistribution = Field(default_factory=VulnerabilityDistribution)
    security_score: float = Field(default=0.0, description="Overall security score 0-100")
    avg_scan_duration: float = Field(default=0.0, description="Average scan duration in seconds")
    cache_hit_rate: float = Field(default=0.0, description="Cache hit rate percentage")
    scan_success_rate: float = Field(default=100.0, description="Scan success rate percentage")
    top_vulnerability_types: List[Dict[str, Any]] = Field(default_factory=list)
    recent_activity: Dict[str, int] = Field(default_factory=dict)

class VulnerabilityTrend(BaseModel):
    """Vulnerability trend data point"""
    timestamp: datetime
    count: int = 0
    severity: SeverityLevel
    repository: Optional[str] = None
    scan_type: str = "single_file"

class RepositoryStats(BaseModel):
    """Statistics for a specific repository"""
    repository_url: str
    repository_name: str
    security_score: float = Field(description="Security score 0-100")
    total_vulnerabilities: int = 0
    vulnerability_distribution: VulnerabilityDistribution = Field(default_factory=VulnerabilityDistribution)
    total_scans: int = 0
    total_files: int = 0
    last_scan_date: Optional[datetime] = None
    languages: List[str] = Field(default_factory=list)
    avg_scan_duration: float = 0.0
    branch: str = "main"

class ScanPerformanceMetrics(BaseModel):
    """Scan performance metrics"""
    scan_type: str
    avg_duration: float = Field(description="Average duration in seconds")
    min_duration: float = Field(description="Minimum duration in seconds") 
    max_duration: float = Field(description="Maximum duration in seconds")
    success_rate: float = Field(description="Success rate percentage")
    total_scans: int = 0
    cache_hit_rate: float = Field(description="Cache hit rate percentage")

class DashboardOverview(BaseModel):
    """Complete dashboard overview data"""
    metrics: SecurityMetrics
    trends: List[VulnerabilityTrend] = Field(default_factory=list)
    top_repositories: List[RepositoryStats] = Field(default_factory=list)
    performance: List[ScanPerformanceMetrics] = Field(default_factory=list)
    time_range: TimeRange
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Export Models
class ExportRequest(BaseModel):
    """Export request configuration"""
    format: ExportFormat
    time_range: TimeRange = TimeRange.LAST_DAY
    include_trends: bool = True
    include_repositories: bool = True
    include_performance: bool = True
    repository_filter: Optional[str] = None
    severity_filter: Optional[SeverityLevel] = None

class ExportResponse(BaseModel):
    """Export response"""
    export_id: str
    status: str
    download_url: Optional[str] = None
    estimated_completion: Optional[datetime] = None

class AlertConfig(BaseModel):
    """Alert configuration (for future use)"""
    enabled: bool = False
    severity_threshold: SeverityLevel = SeverityLevel.HIGH
    webhook_url: Optional[str] = None
    email_recipients: List[str] = Field(default_factory=list)

# CLI-specific models for the new commands
class ScanSummary(BaseModel):
    """Summary data for a specific scan - used by CLI 'audit summary' command"""
    scan_id: str
    timestamp: datetime
    repository: Optional[str] = None
    total_issues: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    security_score: float = 0.0
    scan_duration: Optional[float] = None
    files_scanned: int = 0
    top_rules: List[Dict[str, Any]] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)

class TrendDataPoint(BaseModel):
    """Single data point for trend visualization"""
    date: str  # YYYY-MM-DD format
    total_scans: int = 0
    total_vulnerabilities: int = 0
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0

class HeatmapEntry(BaseModel):
    """Heatmap entry for directory/file visualization"""
    path: str
    rule_hits: int = 0
    severity_score: float = 0.0  # Weighted severity score
    files_count: int = 1

class ScanHistoryEntry(BaseModel):
    """Historical scan entry for 'audit history' command"""
    scan_id: str
    timestamp: datetime
    repository: Optional[str] = None
    total_issues: int = 0
    security_score: float = 0.0
    top_issues: List[str] = Field(default_factory=list)  # Top 3 issue types
    scan_type: str = "single_file"
    duration: Optional[float] = None


class TimeSeries(BaseModel):
    """Time series data point for analytics"""
    timestamp: datetime
    value: float
    label: Optional[str] = None


class MetricsCalculator:
    """Utility class for calculating security metrics and scores"""
    
    def calculate_security_score(self, vulnerability_counts: Dict[str, int], total_files: int) -> float:
        """
        Calculate a security score based on vulnerability counts and file count
        Score ranges from 0-100, where 100 is perfect security
        """
        if total_files == 0:
            return 100.0
        
        # Weight different severity levels
        weights = {
            'CRITICAL': 10,
            'HIGH': 5,
            'MEDIUM': 2,
            'LOW': 1,
            'INFO': 0.5
        }
        
        # Calculate weighted vulnerability score
        weighted_score = 0
        for severity, count in vulnerability_counts.items():
            weight = weights.get(severity.upper(), 1)
            weighted_score += count * weight
        
        # Normalize by file count and convert to 0-100 scale
        if weighted_score == 0:
            return 100.0
        
        # Use logarithmic scale to prevent extreme scores
        import math
        normalized_score = weighted_score / total_files
        security_score = max(0, 100 - (math.log10(normalized_score + 1) * 50))
        
        return round(security_score, 1)

# Phase 9: Additional Models for Advanced Analytics

class ExportRequest(BaseModel):
    """Request model for data export"""
    time_range: Optional[str] = "30d"
    format: ExportFormat = ExportFormat.JSON
    include_trends: bool = True
    include_repositories: bool = True
    include_performance: bool = False

class ExportResponse(BaseModel):
    """Response model for data export"""
    export_id: str
    status: str  # completed, processing, failed, not_implemented
    download_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class AlertConfig(BaseModel):
    """Configuration for automated alerts"""
    name: str
    threshold_type: str  # vulnerability_spike, score_drop, performance_degradation
    threshold_value: float
    time_window: str = "24h"
    webhook_url: Optional[str] = None
    email_recipients: Optional[List[str]] = []
    enabled: bool = True