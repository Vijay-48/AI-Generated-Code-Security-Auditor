"""
Phase 9: Report Generation Utility
Automated report generation with scheduling and export capabilities
"""
import asyncio
import json
import csv
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from io import StringIO

from app.services.analytics_service import analytics_service
from app.models.analytics import TimeRange


class ReportGenerator:
    """Generate scheduled reports and alerts for security analytics"""
    
    def __init__(self):
        self.report_templates = {
            "security_summary": self._generate_security_summary,
            "vulnerability_trends": self._generate_trends_report,
            "performance_analysis": self._generate_performance_report,
            "top_rules_analysis": self._generate_top_rules_report
        }
    
    async def generate_scheduled_report(
        self, 
        report_type: str = "security_summary",
        time_range: TimeRange = TimeRange.LAST_WEEK,
        format_type: str = "markdown",
        save_path: Optional[str] = None
    ) -> str:
        """Generate a comprehensive scheduled report"""
        
        if report_type not in self.report_templates:
            raise ValueError(f"Unknown report type: {report_type}")
        
        # Generate the report content
        report_generator = self.report_templates[report_type]
        report_data = await report_generator(time_range)
        
        # Format the report
        if format_type == "markdown":
            content = self._format_markdown_report(report_data, report_type)
        elif format_type == "json":
            content = json.dumps(report_data, indent=2, default=str)
        elif format_type == "csv":
            content = self._format_csv_report(report_data, report_type)
        else:
            content = self._format_text_report(report_data, report_type)
        
        # Save if path provided
        if save_path:
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w') as f:
                f.write(content)
        
        return content
    
    async def _generate_security_summary(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate comprehensive security summary"""
        overview = await analytics_service.get_dashboard_overview(time_range)
        trends = await analytics_service.get_vulnerability_trends(time_range)
        repositories = await analytics_service.get_repository_stats(10)
        
        return {
            "report_type": "security_summary",
            "time_range": time_range.value,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "metrics": overview.metrics.model_dump() if overview.metrics else {},
            "trends_summary": {
                "total_data_points": len(trends),
                "severity_distribution": self._analyze_trends_severity(trends)
            },
            "top_repositories": [repo.model_dump() for repo in repositories[:5]],
            "key_insights": self._generate_insights(overview.metrics, trends, repositories)
        }
    
    async def _generate_trends_report(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate vulnerability trends analysis"""
        trends = await analytics_service.get_vulnerability_trends(time_range)
        
        # Group trends by severity for analysis
        severity_trends = {}
        for trend in trends:
            severity = trend.severity.value
            if severity not in severity_trends:
                severity_trends[severity] = []
            severity_trends[severity].append({
                "timestamp": trend.timestamp.isoformat(),
                "count": trend.count,
                "repository": trend.repository
            })
        
        return {
            "report_type": "vulnerability_trends",
            "time_range": time_range.value,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "trends_by_severity": severity_trends,
            "total_vulnerabilities": sum(trend.count for trend in trends),
            "peak_day": self._find_peak_vulnerability_day(trends),
            "growth_analysis": self._analyze_growth_patterns(trends)
        }
    
    async def _generate_performance_report(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate performance analysis report"""
        performance_metrics = await analytics_service.get_performance_metrics()
        
        return {
            "report_type": "performance_analysis",
            "time_range": time_range.value,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "scan_performance": [metric.model_dump() for metric in performance_metrics],
            "optimization_recommendations": self._generate_performance_recommendations(performance_metrics)
        }
    
    async def _generate_top_rules_report(self, time_range: TimeRange) -> Dict[str, Any]:
        """Generate top vulnerability rules report"""
        # This would require a direct database query
        session = analytics_service.get_db_session()
        
        from sqlalchemy import func, desc, and_
        from app.models.analytics import ScanRecord, RuleHitRecord
        
        # Calculate time window
        end_time = datetime.now(timezone.utc)
        start_time = analytics_service._get_start_time(end_time, time_range)
        
        # Get top rules
        top_rules = session.query(
            RuleHitRecord.rule_name,
            RuleHitRecord.severity,
            RuleHitRecord.tool,
            func.sum(RuleHitRecord.hit_count).label('total_hits'),
            func.count(func.distinct(RuleHitRecord.scan_id)).label('scan_count')
        ).join(
            ScanRecord, RuleHitRecord.scan_id == ScanRecord.id
        ).filter(
            and_(
                ScanRecord.timestamp >= start_time,
                ScanRecord.timestamp <= end_time
            )
        ).group_by(
            RuleHitRecord.rule_name,
            RuleHitRecord.severity,
            RuleHitRecord.tool
        ).order_by(
            desc('total_hits')
        ).limit(20).all()
        
        session.close()
        
        return {
            "report_type": "top_rules_analysis",
            "time_range": time_range.value,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "top_rules": [
                {
                    "rule_name": rule.rule_name,
                    "severity": rule.severity,
                    "tool": rule.tool,
                    "total_hits": int(rule.total_hits),
                    "scan_count": int(rule.scan_count)
                }
                for rule in top_rules
            ],
            "rule_insights": self._analyze_rule_patterns(top_rules)
        }
    
    def _format_markdown_report(self, data: Dict[str, Any], report_type: str) -> str:
        """Format report data as Markdown"""
        lines = []
        
        # Header
        lines.append(f"# 🛡️ Security Analytics Report - {report_type.replace('_', ' ').title()}")
        lines.append(f"**Generated:** {data['generated_at']}")
        lines.append(f"**Time Range:** {data['time_range']}")
        lines.append("")
        
        if report_type == "security_summary":
            return self._format_security_summary_markdown(data, lines)
        elif report_type == "vulnerability_trends":
            return self._format_trends_markdown(data, lines)
        elif report_type == "performance_analysis":
            return self._format_performance_markdown(data, lines)
        elif report_type == "top_rules_analysis":
            return self._format_top_rules_markdown(data, lines)
        
        return "\n".join(lines)
    
    def _format_security_summary_markdown(self, data: Dict[str, Any], lines: List[str]) -> str:
        """Format security summary as Markdown"""
        metrics = data.get('metrics', {})
        
        lines.append("## 📊 Security Metrics Overview")
        lines.append("")
        lines.append(f"- **Total Scans:** {metrics.get('total_scans', 0):,}")
        lines.append(f"- **Files Analyzed:** {metrics.get('total_files', 0):,}")
        lines.append(f"- **Repositories:** {metrics.get('total_repositories', 0):,}")
        lines.append(f"- **Average Security Score:** {metrics.get('security_score', 0)}/100")
        lines.append("")
        
        # Vulnerability distribution
        vuln_dist = metrics.get('vulnerability_distribution', {})
        lines.append("### 🚨 Vulnerability Distribution")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|----------|--------|")
        lines.append(f"| ⚫ Critical | {vuln_dist.get('critical', 0)} |")
        lines.append(f"| 🔴 High | {vuln_dist.get('high', 0)} |")
        lines.append(f"| 🟡 Medium | {vuln_dist.get('medium', 0)} |")
        lines.append(f"| 🟢 Low | {vuln_dist.get('low', 0)} |")
        lines.append(f"| **Total** | **{vuln_dist.get('total', 0)}** |")
        lines.append("")
        
        # Top repositories
        top_repos = data.get('top_repositories', [])
        if top_repos:
            lines.append("### 🏆 Top Performing Repositories")
            lines.append("")
            lines.append("| Repository | Security Score | Vulnerabilities |")
            lines.append("|------------|----------------|-----------------|")
            for repo in top_repos:
                repo_name = repo.get('repository_name', 'Unknown')[:30]
                score = repo.get('security_score', 0)
                vulns = repo.get('total_vulnerabilities', 0)
                lines.append(f"| {repo_name} | {score:.1f}/100 | {vulns} |")
            lines.append("")
        
        # Key insights
        insights = data.get('key_insights', [])
        if insights:
            lines.append("### 💡 Key Insights")
            lines.append("")
            for insight in insights:
                lines.append(f"- {insight}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_trends_markdown(self, data: Dict[str, Any], lines: List[str]) -> str:
        """Format trends report as Markdown"""
        lines.append("## 📈 Vulnerability Trends Analysis")
        lines.append("")
        lines.append(f"**Total Vulnerabilities:** {data.get('total_vulnerabilities', 0)}")
        
        peak_day = data.get('peak_day')
        if peak_day:
            lines.append(f"**Peak Day:** {peak_day['date']} ({peak_day['count']} vulnerabilities)")
        lines.append("")
        
        # Trends by severity
        severity_trends = data.get('trends_by_severity', {})
        lines.append("### Severity Breakdown")
        lines.append("")
        for severity, trends in severity_trends.items():
            total = sum(t['count'] for t in trends)
            lines.append(f"- **{severity.upper()}:** {total} vulnerabilities across {len(trends)} data points")
        lines.append("")
        
        return "\n".join(lines)
    
    def _format_performance_markdown(self, data: Dict[str, Any], lines: List[str]) -> str:
        """Format performance report as Markdown"""
        lines.append("## ⚡ Performance Analysis")
        lines.append("")
        
        scan_performance = data.get('scan_performance', [])
        if scan_performance:
            lines.append("### Scan Performance Metrics")
            lines.append("")
            lines.append("| Scan Type | Avg Duration (s) | Success Rate | Total Scans |")
            lines.append("|-----------|------------------|--------------|-------------|")
            for perf in scan_performance:
                lines.append(f"| {perf['scan_type']} | {perf['avg_duration']:.2f} | {perf['success_rate']:.1f}% | {perf['total_scans']} |")
            lines.append("")
        
        recommendations = data.get('optimization_recommendations', [])
        if recommendations:
            lines.append("### 🚀 Optimization Recommendations")
            lines.append("")
            for rec in recommendations:
                lines.append(f"- {rec}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_top_rules_markdown(self, data: Dict[str, Any], lines: List[str]) -> str:
        """Format top rules report as Markdown"""
        lines.append("## 🔝 Top Vulnerability Rules")
        lines.append("")
        
        top_rules = data.get('top_rules', [])
        if top_rules:
            lines.append("| Rank | Rule | Severity | Tool | Total Hits | Scans |")
            lines.append("|------|------|----------|------|------------|-------|")
            for i, rule in enumerate(top_rules[:10], 1):
                severity_emoji = {'critical': '⚫', 'high': '🔴', 'medium': '🟡', 'low': '🟢'}.get(rule['severity'], '🔍')
                lines.append(f"| {i} | {rule['rule_name'][:25]} | {severity_emoji} {rule['severity']} | {rule['tool']} | {rule['total_hits']} | {rule['scan_count']} |")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_csv_report(self, data: Dict[str, Any], report_type: str) -> str:
        """Format report data as CSV"""
        output = StringIO()
        
        if report_type == "security_summary":
            writer = csv.writer(output)
            metrics = data.get('metrics', {})
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Scans', metrics.get('total_scans', 0)])
            writer.writerow(['Total Files', metrics.get('total_files', 0)])
            writer.writerow(['Security Score', metrics.get('security_score', 0)])
            
        elif report_type == "top_rules_analysis":
            writer = csv.writer(output)
            writer.writerow(['Rule Name', 'Severity', 'Tool', 'Total Hits', 'Scan Count'])
            for rule in data.get('top_rules', []):
                writer.writerow([
                    rule['rule_name'],
                    rule['severity'],
                    rule['tool'],
                    rule['total_hits'],
                    rule['scan_count']
                ])
        
        return output.getvalue()
    
    def _format_text_report(self, data: Dict[str, Any], report_type: str) -> str:
        """Format report data as plain text"""
        # Simple text formatting - could be enhanced
        return json.dumps(data, indent=2, default=str)
    
    # Helper methods for data analysis
    
    def _analyze_trends_severity(self, trends) -> Dict[str, int]:
        """Analyze severity distribution in trends"""
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for trend in trends:
            severity = trend.severity.value
            if severity in severity_counts:
                severity_counts[severity] += trend.count
        return severity_counts
    
    def _find_peak_vulnerability_day(self, trends) -> Optional[Dict[str, Any]]:
        """Find the day with highest vulnerability count"""
        if not trends:
            return None
        
        peak_trend = max(trends, key=lambda t: t.count)
        return {
            "date": peak_trend.timestamp.strftime('%Y-%m-%d'),
            "count": peak_trend.count
        }
    
    def _analyze_growth_patterns(self, trends) -> Dict[str, Any]:
        """Analyze vulnerability growth patterns"""
        if len(trends) < 2:
            return {"trend": "insufficient_data"}
        
        # Simple growth analysis
        first_half = trends[:len(trends)//2]
        second_half = trends[len(trends)//2:]
        
        first_avg = sum(t.count for t in first_half) / len(first_half)
        second_avg = sum(t.count for t in second_half) / len(second_half)
        
        growth_rate = ((second_avg - first_avg) / first_avg * 100) if first_avg > 0 else 0
        
        return {
            "growth_rate_percent": round(growth_rate, 1),
            "trend": "increasing" if growth_rate > 10 else "decreasing" if growth_rate < -10 else "stable"
        }
    
    def _generate_insights(self, metrics, trends, repositories) -> List[str]:
        """Generate key insights from the data"""
        insights = []
        
        if metrics:
            # Security score insight
            security_score = metrics.security_score or 0
            if security_score > 80:
                insights.append("🟢 Overall security posture is strong with high security scores")
            elif security_score > 60:
                insights.append("🟡 Security posture is moderate, some improvements needed")
            else:
                insights.append("🔴 Security posture needs immediate attention")
            
            # Vulnerability distribution insight
            vuln_dist = metrics.vulnerability_distribution
            if vuln_dist and vuln_dist.critical > 0:
                insights.append(f"⚠️ {vuln_dist.critical} critical vulnerabilities require immediate remediation")
        
        # Repository insights
        if repositories:
            top_repo = repositories[0]
            insights.append(f"🏆 Best performing repository: {top_repo.repository_name} (Score: {top_repo.security_score:.1f})")
        
        return insights
    
    def _generate_performance_recommendations(self, performance_metrics) -> List[str]:
        """Generate performance optimization recommendations"""
        recommendations = []
        
        for metric in performance_metrics:
            if metric.avg_duration > 60:  # More than 1 minute
                recommendations.append(f"Consider optimizing {metric.scan_type} scans (avg: {metric.avg_duration:.1f}s)")
            
            if metric.success_rate < 95:
                recommendations.append(f"Investigate failures in {metric.scan_type} scans (success rate: {metric.success_rate:.1f}%)")
        
        if not recommendations:
            recommendations.append("Performance metrics are within acceptable ranges")
        
        return recommendations
    
    def _analyze_rule_patterns(self, top_rules) -> List[str]:
        """Analyze patterns in top vulnerability rules"""
        insights = []
        
        if not top_rules:
            return ["No rule data available for analysis"]
        
        # Analyze by severity
        severity_counts = {}
        tool_counts = {}
        
        for rule in top_rules:
            severity = rule.severity
            tool = rule.tool
            
            severity_counts[severity] = severity_counts.get(severity, 0) + rule.total_hits
            tool_counts[tool] = tool_counts.get(tool, 0) + rule.total_hits
        
        # Top severity
        if severity_counts:
            top_severity = max(severity_counts.items(), key=lambda x: x[1])
            insights.append(f"Most common severity: {top_severity[0]} ({top_severity[1]} hits)")
        
        # Top tool
        if tool_counts:
            top_tool = max(tool_counts.items(), key=lambda x: x[1])
            insights.append(f"Most active scanning tool: {top_tool[0]} ({top_tool[1]} hits)")
        
        return insights


# Global report generator instance
report_generator = ReportGenerator()


async def generate_weekly_report() -> str:
    """Generate weekly security report"""
    return await report_generator.generate_scheduled_report(
        report_type="security_summary",
        time_range=TimeRange.LAST_WEEK,
        format_type="markdown"
    )


async def generate_performance_report() -> str:
    """Generate performance optimization report"""
    return await report_generator.generate_scheduled_report(
        report_type="performance_analysis",
        time_range=TimeRange.LAST_MONTH,
        format_type="markdown"
    )