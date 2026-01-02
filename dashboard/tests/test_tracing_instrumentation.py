import sys
import types
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

from dashboard import tracing_setup


def test_enable_auto_instrumentation_httpx_new(monkeypatch):
    """HTTPXClientInstrumentor should be invoked when available."""
    m = types.ModuleType("opentelemetry.instrumentation.httpx")
    calls = {"count": 0}

    class HTTPXClientInstrumentor:
        def instrument(self):
            calls["count"] += 1
            return None

    m.HTTPXClientInstrumentor = HTTPXClientInstrumentor
    monkeypatch.setitem(sys.modules, "opentelemetry.instrumentation.httpx", m)

    # Should run without raising
    tracing_setup.enable_auto_instrumentation()
    assert calls["count"] == 1


def test_enable_auto_instrumentation_httpx_old(monkeypatch):
    """HttpxInstrumentor should be invoked when available."""
    m = types.ModuleType("opentelemetry.instrumentation.httpx")
    calls = {"count": 0}

    class HttpxInstrumentor:
        def instrument(self):
            calls["count"] += 1
            return None

    m.HttpxInstrumentor = HttpxInstrumentor
    monkeypatch.setitem(sys.modules, "opentelemetry.instrumentation.httpx", m)

    # Should run without raising
    tracing_setup.enable_auto_instrumentation()
    assert calls["count"] == 1


def test_enable_auto_instrumentation_httpx_missing(monkeypatch):
    """If the httpx instrumentation module is missing, it should no-op."""
    real_import = tracing_setup.importlib.import_module

    def fake_import(name):
        if name == "opentelemetry.instrumentation.httpx":
            raise ImportError("missing module")
        return real_import(name)

    monkeypatch.setattr(tracing_setup.importlib, "import_module", fake_import)

    tracing_setup.enable_auto_instrumentation()


def test_enable_auto_instrumentation_httpx_no_instrumentor(monkeypatch):
    """If the module lacks instrumentors, it should no-op."""
    m = types.ModuleType("opentelemetry.instrumentation.httpx")
    monkeypatch.setitem(sys.modules, "opentelemetry.instrumentation.httpx", m)

    tracing_setup.enable_auto_instrumentation()


def test_init_tracing_preserves_existing_provider(monkeypatch):
    """Reuse existing TracerProvider instead of overriding it.

    The OpenTelemetry API can refuse global provider overrides, so we
    monkeypatch `trace.get_tracer_provider` to return a TracerProvider
    instance and assert `init_tracing` uses it.
    """
    existing = TracerProvider()

    # Ensure init_tracing observes an existing provider and does not
    # attempt to override it.
    monkeypatch.setattr(trace, "get_tracer_provider", lambda: existing)

    ret = tracing_setup.init_tracing()
    assert ret is existing
    assert trace.get_tracer_provider() is existing
