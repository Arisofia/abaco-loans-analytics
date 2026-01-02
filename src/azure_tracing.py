"""
Azure Application Insights Tracing Integration
Enables distributed tracing, logging, and metrics collection for the analytics dashboard
"""

import logging
import os

from opencensus.ext.azure.log_exporter import AzureLogHandler
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.trace.samplers import ProbabilitySampler
from opencensus.trace.tracer import Tracer


def setup_azure_tracing():
    """Initialize Azure Application Insights tracing."""

    connection_string = os.getenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "InstrumentationKey=00000000-0000-0000-0000-000000000000",
    )

    # Configure logging handler
    handler = AzureLogHandler(connection_string=connection_string)
    handler.setLevel(logging.INFO)

    # Configure formatter
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Add handler to root logger
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    # Configure trace exporter
    trace_exporter = AzureExporter(connection_string=connection_string)
    tracer = Tracer(
        exporter=trace_exporter,
        sampler=ProbabilitySampler(rate=1.0),  # Sample 100% in development, adjust for production
    )

    return logger, tracer


def trace_analytics_job(job_name: str, client_id: str, run_id: str):
    """Decorator for tracing analytics batch jobs."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            _, tracer = setup_azure_tracing()
            logger = logging.getLogger(__name__)

            with tracer.span(name=f"{job_name}.{run_id}") as span:
                span.add_attribute("client_id", client_id)
                span.add_attribute("run_id", run_id)
                span.add_attribute("job_name", job_name)

                logger.info(
                    f"[TRACE] Starting job: {job_name} | client_id={client_id} | run_id={run_id}"
                )
                try:
                    result = func(*args, **kwargs)
                    logger.info(f"[TRACE] Job completed: {job_name}")
                    span.add_attribute("status", "success")
                    return result
                except Exception as e:
                    logger.error(f"[TRACE] Job failed: {job_name} | error={str(e)}")
                    span.add_attribute("status", "failed")
                    span.add_attribute("error", str(e))
                    raise

        return wrapper

    return decorator


# Example usage in batch runner
if __name__ == "__main__":
    logger, tracer = setup_azure_tracing()
    logger.info("Azure Application Insights tracing initialized")
