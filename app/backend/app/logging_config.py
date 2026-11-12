import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

# İstek boyunca yazılan tüm log satırlarına aynı trace_id eklenir
trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)

EXTRA_FIELDS = ("method", "path", "status", "duration_ms")

_base_record_factory = logging.getLogRecordFactory()


def _record_factory(*args, **kwargs) -> logging.LogRecord:
    # trace_id, log yazıldığı anda kaydın içine konur
    record = _base_record_factory(*args, **kwargs)
    record.trace_id = trace_id_var.get()
    return record


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
        }
        for field in EXTRA_FIELDS:
            if hasattr(record, field):
                entry[field] = getattr(record, field)
        if record.exc_info:
            entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def setup_logging(level: str) -> None:
    logging.setLogRecordFactory(_record_factory)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())

    # Uvicorn logları da aynı JSON formatında yazılsın
    for name in ("uvicorn", "uvicorn.error"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers = []
        uvicorn_logger.propagate = True

    # İstek logunu request_logging middleware'i yazıyor; access log tekrar etmesin
    logging.getLogger("uvicorn.access").disabled = True
