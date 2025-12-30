"""
Tracing setup for Python using Azure Monitor OpenTelemetry.

This module provides observability and distributed tracing for the Abaco Analytics workspace
using Azure Application Insights via OpenTelemetry.

Usage:
    from python.tracing_setup import configure_tracing, get_tracer
    
    # Configure tracing once at application startup
    configure_tracing()
    
    # Get a tracer for your module
    tracer = get_tracer(__name__)
    
    # Use spans to trace operations
    with tracer.start_as_current_span("operation_name"):
        # Your code here
        pass
"""

import logging
import os
from typing import Optional

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import trace
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

logger = logging.getLogger(__name__)

_configured = False


def configure_tracing(connection_string: Optional[str] = None) -> None:
    """
    Configure Azure Monitor OpenTelemetry tracing.
    
    This should be called once at application startup before any operations are traced.
    
    Args:
        connection_string: Azure Application Insights connection string. 
                          If not provided, will read from APPLICATIONINSIGHTS_CONNECTION_STRING 
                          environment variable.
    """
    global _configured
    
    if _configured:
        logger.debug("Tracing already configured, skipping")
        return
    
    # Get connection string from parameter or environment variable
    conn_string = connection_string or os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
    
    if not conn_string:
        logger.warning(
            "No Application Insights connection string provided. "
            "Tracing will be disabled. Set APPLICATIONINSIGHTS_CONNECTION_STRING environment variable."
        )
        return
    
    try:
        # Configure Azure Monitor with OpenTelemetry
        configure_azure_monitor(connection_string=conn_string)
        
        # Instrument common HTTP libraries
        RequestsInstrumentor().instrument()
        URLLib3Instrumentor().instrument()
        
        _configured = True
        logger.info("Azure Monitor tracing configured successfully")
    except Exception as e:
        logger.error(f"Failed to configure Azure Monitor tracing: {e}")


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a tracer for the specified module.
    
    Args:
        name: Name of the module (typically __name__)
        
    Returns:
        OpenTelemetry Tracer instance
    """
    return trace.get_tracer(name)


def is_tracing_enabled() -> bool:
    """Check if tracing has been configured and is enabled."""
    return _configured
