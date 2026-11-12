import logging
import time
import uuid

from fastapi import Request, Response

from app.logging_config import trace_id_var

logger = logging.getLogger("app.request")

# Kubernetes probe'ları ve Prometheus istekleri logları kirletmesin
SKIPPED_PATHS = {"/healthz", "/readyz", "/metrics"}


async def log_requests(request: Request, call_next) -> Response:
    if request.url.path in SKIPPED_PATHS:
        return await call_next(request)

    trace_id = uuid.uuid4().hex
    token = trace_id_var.set(trace_id)
    start = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        # İstemci bir hatayı bildirirken bu değeri verirse loglarda aranabilir
        response.headers["X-Trace-ID"] = trace_id
        return response
    except Exception:
        logger.exception("unhandled error")
        raise
    finally:
        logger.info(
            "request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status": status,
                "duration_ms": round((time.perf_counter() - start) * 1000, 2),
            },
        )
        trace_id_var.reset(token)
