from fastapi import Request, Response
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import time

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
AUDIT_COUNT = Counter('audits_total', 'Total security audits performed', ['language', 'model'])
VULNERABILITY_COUNT = Counter('vulnerabilities_found_total', 'Total vulnerabilities found', ['severity', 'tool'])
ACTIVE_SCANS = Gauge('active_scans', 'Number of active security scans')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive)
        start_time = time.time()
        
        ACTIVE_SCANS.inc()
        
        # Create response wrapper
        response_sent = False
        status_code = 200
        
        async def send_wrapper(message):
            nonlocal response_sent, status_code
            if message["type"] == "http.response.start":
                status_code = message["status"]
            elif message["type"] == "http.response.body" and not response_sent:
                response_sent = True
                # Record metrics
                duration = time.time() - start_time
                REQUEST_DURATION.observe(duration)
                REQUEST_COUNT.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=status_code
                ).inc()
                ACTIVE_SCANS.dec()
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)

def record_audit_metrics(language: str, model: str, vulnerabilities: list):
    """Record metrics for completed audits"""
    AUDIT_COUNT.labels(language=language, model=model.split('/')[0]).inc()
    
    for vuln in vulnerabilities:
        VULNERABILITY_COUNT.labels(
            severity=vuln.get('severity', 'unknown'),
            tool=vuln.get('tool', 'unknown')
        ).inc()

async def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)