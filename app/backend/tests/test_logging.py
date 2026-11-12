import json
import logging
import sys

from app.logging_config import JsonFormatter


def request_logs(caplog):
    return [r for r in caplog.records if r.getMessage() == "request completed"]


def make_record(message, level=logging.INFO, exc_info=None):
    return logging.LogRecord("app", level, __file__, 1, message, (), exc_info)


def test_response_has_trace_id_header(client):
    response = client.get("/api/todos")

    assert len(response.headers["X-Trace-ID"]) == 32


def test_request_is_logged_with_details(client, caplog):
    with caplog.at_level(logging.INFO):
        response = client.get("/api/todos")

    record = request_logs(caplog)[-1]
    assert record.method == "GET"
    assert record.path == "/api/todos"
    assert record.status == 200
    assert record.duration_ms >= 0
    assert record.trace_id == response.headers["X-Trace-ID"]


def test_application_logs_share_trace_id_of_request(client, caplog):
    with caplog.at_level(logging.INFO):
        response = client.post("/api/todos", json={"title": "trace test"})

    created = next(r for r in caplog.records if r.getMessage().startswith("todo created"))
    assert created.trace_id == response.headers["X-Trace-ID"]


def test_each_request_gets_a_new_trace_id(client):
    first = client.get("/api/todos").headers["X-Trace-ID"]
    second = client.get("/api/todos").headers["X-Trace-ID"]

    assert first != second


def test_probe_endpoints_are_not_logged(client, caplog):
    with caplog.at_level(logging.INFO):
        client.get("/healthz")
        client.get("/metrics")

    assert request_logs(caplog) == []


def test_json_formatter_writes_valid_json():
    record = make_record("hello")
    record.trace_id = "abc123"
    record.status = 201

    entry = json.loads(JsonFormatter().format(record))

    assert entry["level"] == "INFO"
    assert entry["message"] == "hello"
    assert entry["trace_id"] == "abc123"
    assert entry["status"] == 201
    assert "timestamp" in entry


def test_json_formatter_includes_exception():
    try:
        raise ValueError("boom")
    except ValueError:
        record = make_record("failed", logging.ERROR, sys.exc_info())

    entry = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in entry["exception"]
