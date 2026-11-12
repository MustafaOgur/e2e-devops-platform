import time

from fastapi import Request, Response
from prometheus_client import Counter, Histogram

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)

# Kubernetes probe'ları ve Prometheus'un kendi istekleri metrikleri kirletmesin
SKIPPED_PATHS = {"/healthz", "/readyz", "/metrics"}


async def record_metrics(request: Request, call_next) -> Response:
    if request.url.path in SKIPPED_PATHS:
        return await call_next(request)

    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        # /api/todos/5 yerine /api/todos/{todo_id}: etiket sayısı sınırsız büyümesin
        route = request.scope.get("route")
        path = route.path if route else "unmatched"
        REQUEST_COUNT.labels(request.method, path, str(status)).inc()
        REQUEST_LATENCY.labels(request.method, path).observe(time.perf_counter() - start)
