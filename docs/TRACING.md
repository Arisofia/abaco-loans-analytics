# Tracing and Observability Setup

This document describes how tracing and observability are implemented in the Abaco Analytics workspace using Azure Monitor OpenTelemetry.

## Overview

The workspace uses **Azure Monitor OpenTelemetry** for distributed tracing and observability. This provides:

- **Distributed tracing** across pipeline phases, agent executions, and data transformations
- **Performance monitoring** with detailed timing and metrics
- **Error tracking** with stack traces and context
- **Integration with Azure Application Insights** for visualization and alerting

## Configuration

### Prerequisites

1. Azure Application Insights instance
2. Application Insights Connection String

### Environment Variables

Set the following environment variable to enable tracing:

```bash
export APPLICATIONINSIGHTS_CONNECTION_STRING="InstrumentationKey=...;IngestionEndpoint=..."
```

You can find this connection string in the Azure Portal:
1. Navigate to your Application Insights resource
2. Go to "Overview" or "Properties"
3. Copy the "Connection String"

### Dependencies

The following packages are required and included in `requirements.txt`:

```
azure-monitor-opentelemetry>=1.0.0
azure-identity>=1.12.0
```

## Usage

### Initializing Tracing

In your application entry point (e.g., `main.py`, dashboard startup, or pipeline script):

```python
from python.tracing_setup import configure_tracing

# Configure tracing once at startup
configure_tracing()
```

### Using Tracing in Code

Import the tracer and use spans to trace operations:

```python
from python.tracing_setup import get_tracer

tracer = get_tracer(__name__)

def my_function():
    with tracer.start_as_current_span("my_operation") as span:
        # Add custom attributes for better context
        span.set_attribute("operation.type", "data_processing")
        span.set_attribute("row_count", 1000)
        
        # Your code here
        result = process_data()
        
        # Record exceptions if they occur
        try:
            risky_operation()
        except Exception as e:
            span.record_exception(e)
            raise
        
        return result
```

### Nested Spans

You can create nested spans to trace sub-operations:

```python
def pipeline_execute():
    with tracer.start_as_current_span("pipeline.execute") as parent_span:
        parent_span.set_attribute("pipeline.run_id", "run_123")
        
        with tracer.start_as_current_span("pipeline.ingestion"):
            # Ingestion code
            pass
        
        with tracer.start_as_current_span("pipeline.transformation"):
            # Transformation code
            pass
        
        with tracer.start_as_current_span("pipeline.calculation"):
            # Calculation code
            pass
```

## Where Tracing is Implemented

Tracing has been integrated into the following modules:

1. **Agent Orchestrator** (`python/agents/orchestrator.py`)
   - Traces agent execution with retry attempts
   - Records agent name, role, and performance metrics
   - Tracks input data hash and output quality

2. **Pipeline Orchestrator** (`python/pipeline/orchestrator.py`)
   - Traces complete pipeline execution
   - Tracks each phase: ingestion, transformation, calculation, compliance, output
   - Records row counts, masked columns, and metrics

## Observability Workflows

The `.github/workflows/opik-observability.yml` workflow runs daily to:

1. **Fetch system metrics** - Collects observability data
2. **Analyze pipeline health** - Checks pipeline success rates
3. **Analyze agent performance** - Monitors agent response times
4. **Check data quality trends** - Tracks data quality scores
5. **Generate dashboard** - Creates HTML dashboard
6. **Send alerts** - Notifies on critical issues

## Viewing Traces

### Azure Portal

1. Navigate to your Application Insights resource
2. Go to "Transaction search" or "Application map"
3. Filter by operation name (e.g., `pipeline.execute`, `agent_orchestrator.run`)
4. View detailed traces with timing and custom attributes

### Query with KQL

Use Kusto Query Language (KQL) to query traces:

```kql
// Find slow pipeline executions
traces
| where operation_Name == "pipeline.execute"
| where duration > 60000  // > 60 seconds
| project timestamp, duration, customDimensions
| order by duration desc

// Agent execution metrics
traces
| where operation_Name startswith "agent"
| summarize avg(duration), count() by operation_Name
| order by avg_duration desc
```

## Troubleshooting

### Tracing Not Working

1. **Check connection string**: Verify `APPLICATIONINSIGHTS_CONNECTION_STRING` is set correctly
2. **Check initialization**: Ensure `configure_tracing()` is called at startup
3. **Check logs**: Look for "Azure Monitor tracing configured successfully" message

### Missing Traces

- Traces are batched and sent asynchronously
- It may take 1-2 minutes for traces to appear in Azure
- Check network connectivity to Azure endpoints

### High Overhead

- Tracing adds minimal overhead (<1% typically)
- Adjust sampling if needed (see Azure Monitor documentation)
- Consider disabling tracing in non-production environments

## Best Practices

1. **Use meaningful span names**: Use descriptive operation names like `pipeline.ingestion` not `step1`
2. **Add relevant attributes**: Include context like `run_id`, `user`, `row_count`
3. **Record exceptions**: Always use `span.record_exception(e)` for error tracking
4. **Keep spans focused**: Each span should represent a single logical operation
5. **Use nested spans**: Create child spans for sub-operations

## Security Notes

- Connection strings contain sensitive credentials
- Never commit connection strings to source control
- Use environment variables or Azure Key Vault
- Rotate connection strings periodically
- Traces may contain PII - ensure compliance with data policies

## Further Reading

- [Azure Monitor OpenTelemetry Python Documentation](https://learn.microsoft.com/en-us/azure/azure-monitor/app/opentelemetry-enable?tabs=python)
- [OpenTelemetry Python SDK](https://opentelemetry.io/docs/instrumentation/python/)
- [Application Insights Overview](https://learn.microsoft.com/en-us/azure/azure-monitor/app/app-insights-overview)
