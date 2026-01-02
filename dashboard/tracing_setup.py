"""OpenTelemetry tracing setup for Abaco Analytics (dashboard-local copy).

This file lives in the Streamlit app root so the dashboard can be deployed as
its own App Service project root (i.e., deploy ./dashboard).

Configures distributed tracing with support for:
- Azure Application Insights (via OTLP exporter)
- Local OTEL collector (fallback)
- Auto-instrumentation of common libraries (httpx, requests, etc.)
"""

import importlib
import logging
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)


def init_tracing(
    service_name: str = "abaco-dashboard",
    service_version: str = "1.0.0",
    otlp_endpoint: Optional[str] = None,
) -> TracerProvider:
    existing_provider = trace.get_tracer_provider()
    if isinstance(existing_provider, TracerProvider):
        tracer_provider = existing_provider
    else:
        resource = Resource.create(
            {
                "service.name": service_name,
                "service.version": service_version,
            }
        )
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

    if otlp_endpoint is None:
        otlp_endpoint = os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            "http://localhost:4318",
        )

    try:
        exporter = OTLPSpanExporter(endpoint=otlp_endpoint)
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info(
            "OTEL tracing initialized with endpoint: %s",
            otlp_endpoint,
        )
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Failed to initialize OTEL exporter for %s: %s",
            otlp_endpoint,
            str(exc),
        )

    return tracer_provider


def enable_auto_instrumentation() -> None:
    instrumented = []

    try:
        httpx_module = importlib.import_module(
            "opentelemetry.instrumentation.httpx"
        )
        httpx_instrumentor = None
        if hasattr(httpx_module, "HTTPXClientInstrumentor"):
            httpx_instrumentor = httpx_module.HTTPXClientInstrumentor()
        elif hasattr(httpx_module, "HttpxInstrumentor"):
            httpx_instrumentor = httpx_module.HttpxInstrumentor()
        if httpx_instrumentor:
            httpx_instrumentor.instrument()
            instrumented.append("httpx")
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Auto-instrumentation setup failed for httpx: %s",
            str(exc),
        )

    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        RequestsInstrumentor().instrument()
        instrumented.append("requests")
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Auto-instrumentation setup failed for requests: %s",
            str(exc),
        )

    try:
        from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

        URLLib3Instrumentor().instrument()
        instrumented.append("urllib3")
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Auto-instrumentation setup failed for urllib3: %s",
            str(exc),
        )

    try:
        from opentelemetry.instrumentation.sqlite3 import SQLite3Instrumentor

        SQLite3Instrumentor().instrument()
        instrumented.append("sqlite3")
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Auto-instrumentation setup failed for sqlite3: %s",
            str(exc),
        )

    try:
        from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor

        Psycopg2Instrumentor().instrument()
        instrumented.append("psycopg2")
    except Exception:
        pass

    try:
        from opentelemetry.instrumentation.psycopg import PsycopgInstrumentor

        PsycopgInstrumentor().instrument()
        instrumented.append("psycopg")
    except Exception:
        pass

    if instrumented:
        logger.info(
            "Auto-instrumentation enabled for: %s", ", ".join(instrumented)
        )


def get_tracer(name: str = __name__) -> trace.Tracer:
    return trace.get_tracer(name)


if not isinstance(trace.get_tracer_provider(), TracerProvider):
    try:
        init_tracing()
        enable_auto_instrumentation()
    except Exception as exc:  # pragma: no cover
        logger.warning(
            "Tracing auto-init failed (will retry on explicit init): %s",
            str(exc),
        )
