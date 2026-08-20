"""Prometheus metrics — request latency/count, cache hit ratio, query timings.

Exposed at `settings.prometheus_metrics_path` (default `/metrics`) by
`main.py`. Kept as plain module-level registries so any layer can import and
increment them without a FastAPI dependency, e.g. the query-execution use
case records `QUERY_DURATION` regardless of which endpoint triggered it.
"""
from __future__ import annotations

from prometheus_client import Counter, Histogram

HTTP_REQUESTS_TOTAL = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status_code"],
)

HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
)

DASHBOARD_QUERY_DURATION_SECONDS = Histogram(
    "dashboard_query_duration_seconds",
    "Time to execute a widget's underlying data query against a datasource",
    ["datasource_type", "cache_status"],  # cache_status: hit|miss|bypass
    buckets=(0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10, 30),
)

QUERY_CACHE_HITS_TOTAL = Counter(
    "query_cache_hits_total", "Redis query-result cache hits", ["module"]
)
QUERY_CACHE_MISSES_TOTAL = Counter(
    "query_cache_misses_total", "Redis query-result cache misses", ["module"]
)
