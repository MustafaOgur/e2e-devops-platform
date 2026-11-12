def get_metrics(client):
    return client.get("/metrics").text


def test_metrics_endpoint_uses_prometheus_format(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")


def test_metrics_count_requests_by_route(client):
    client.get("/api/todos")

    expected = 'http_requests_total{method="GET",path="/api/todos",status="200"}'
    assert expected in get_metrics(client)


def test_metrics_use_route_template_instead_of_raw_path(client):
    client.get("/api/todos/999")

    metrics = get_metrics(client)
    assert 'path="/api/todos/{todo_id}",status="404"' in metrics
    assert 'path="/api/todos/999"' not in metrics


def test_metrics_record_unmatched_routes(client):
    client.get("/does-not-exist")

    assert 'path="unmatched",status="404"' in get_metrics(client)


def test_metrics_record_request_latency(client):
    client.get("/api/todos")

    expected = 'http_request_duration_seconds_count{method="GET",path="/api/todos"}'
    assert expected in get_metrics(client)


def test_metrics_skip_probe_and_metrics_endpoints(client):
    client.get("/healthz")
    client.get("/readyz")

    metrics = get_metrics(client)
    assert 'path="/healthz"' not in metrics
    assert 'path="/readyz"' not in metrics
    assert 'path="/metrics"' not in metrics
