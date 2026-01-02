"""
Tests for the tracing_setup module.

This module tests the OpenTelemetry tracing configuration for Azure Monitor,
including graceful degradation when tracing is unavailable.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestTracingSetup(unittest.TestCase):
    """Test cases for tracing setup functionality."""

    def setUp(self):
        """Reset tracing state before each test."""
        # Clear module cache to ensure fresh import
        if 'python.tracing_setup' in sys.modules:
            del sys.modules['python.tracing_setup']

    def tearDown(self):
        """Clean up after each test."""
        # Clear environment variables
        for var in ['APPLICATIONINSIGHTS_CONNECTION_STRING', 'AZURE_APPINSIGHTS_SERVICE_NAME', 
                    'PIPELINE_ENV', 'PYTHON_ENV']:
            if var in os.environ:
                del os.environ[var]

    def test_configure_tracing_without_connection_string(self):
        """Test that configure_tracing returns False when connection string is not set."""
        from python.tracing_setup import configure_tracing

        result = configure_tracing()
        self.assertFalse(result, "Should return False when APPLICATIONINSIGHTS_CONNECTION_STRING is not set")

    @patch('python.tracing_setup.logger')
    def test_configure_tracing_with_mock_azure_monitor(self, mock_logger):
        """Test successful tracing configuration with mocked Azure Monitor."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'

        # Mock the azure.monitor.opentelemetry module
        mock_azure_monitor = MagicMock()
        mock_configure = MagicMock()
        mock_azure_monitor.configure_azure_monitor = mock_configure

        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry': MagicMock(),
            'opentelemetry.trace': MagicMock()
        }):
            from python.tracing_setup import configure_tracing
            
            result = configure_tracing(service_name="test-service")
            
            self.assertTrue(result, "Should return True when connection string is set")
            mock_configure.assert_called_once()

    def test_service_name_from_environment(self):
        """Test that service name is resolved from environment variables."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'
        os.environ['AZURE_APPINSIGHTS_SERVICE_NAME'] = 'custom-service-name'

        mock_azure_monitor = MagicMock()
        mock_configure = MagicMock()
        mock_azure_monitor.configure_azure_monitor = mock_configure

        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry': MagicMock(),
            'opentelemetry.trace': MagicMock()
        }):
            from python.tracing_setup import configure_tracing

            configure_tracing()
            
            call_args = mock_configure.call_args
            resource_attrs = call_args.kwargs.get('resource_attributes', {})
            self.assertEqual(
                resource_attrs.get('service.name'),
                'custom-service-name',
                "Should use AZURE_APPINSIGHTS_SERVICE_NAME when set"
            )

    def test_environment_name_resolution(self):
        """Test that environment name is resolved correctly from PIPELINE_ENV."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'
        os.environ['PIPELINE_ENV'] = 'production'

        mock_azure_monitor = MagicMock()
        mock_configure = MagicMock()
        mock_azure_monitor.configure_azure_monitor = mock_configure

        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry': MagicMock(),
            'opentelemetry.trace': MagicMock()
        }):
            from python.tracing_setup import configure_tracing

            configure_tracing()
            
            call_args = mock_configure.call_args
            resource_attrs = call_args.kwargs.get('resource_attributes', {})
            self.assertEqual(
                resource_attrs.get('deployment.environment'),
                'production',
                "Should use PIPELINE_ENV for environment"
            )

    def test_prevent_duplicate_initialization(self):
        """Test that configure_tracing prevents duplicate initialization."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'

        mock_azure_monitor = MagicMock()
        mock_configure = MagicMock()
        mock_azure_monitor.configure_azure_monitor = mock_configure

        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry': MagicMock(),
            'opentelemetry.trace': MagicMock()
        }):
            from python.tracing_setup import configure_tracing

            # First call should configure
            result1 = configure_tracing()
            self.assertTrue(result1)
            self.assertEqual(mock_configure.call_count, 1)

            # Second call should skip configuration
            result2 = configure_tracing()
            self.assertTrue(result2)
            self.assertEqual(mock_configure.call_count, 1, "Should not call configure_azure_monitor again")

    def test_handle_import_error(self):
        """Test graceful handling when Azure Monitor packages are not installed."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'

        # Ensure the module cannot import azure.monitor.opentelemetry
        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': None
        }):
            # Force module reload
            if 'python.tracing_setup' in sys.modules:
                del sys.modules['python.tracing_setup']
                
            from python.tracing_setup import configure_tracing

            result = configure_tracing()
            self.assertFalse(result, "Should return False when packages are not installed")

    def test_get_tracer_returns_value(self):
        """Test get_tracer returns None when OpenTelemetry is unavailable."""
        from python.tracing_setup import get_tracer

        import builtins

        original_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name.startswith("opentelemetry"):
                raise ImportError("No module named 'opentelemetry'")
            return original_import(name, *args, **kwargs)

        with patch("builtins.__import__", side_effect=mock_import):
            tracer = get_tracer("test_module")

        self.assertIsNone(tracer, "Should return None when OpenTelemetry is not available")

    def test_get_tracer_with_mocked_opentelemetry(self):
        """Test get_tracer returns tracer when OpenTelemetry is mocked."""
        mock_trace = MagicMock()
        mock_tracer = MagicMock()
        mock_trace.get_tracer.return_value = mock_tracer

        with patch.dict('sys.modules', {'opentelemetry': MagicMock(), 'opentelemetry.trace': mock_trace}):
            # Force module reload
            if 'python.tracing_setup' in sys.modules:
                del sys.modules['python.tracing_setup']
                
            from python.tracing_setup import get_tracer

            tracer = get_tracer("test_module")
            
            self.assertIsNotNone(tracer, "Should return a tracer instance when OpenTelemetry is available")

    def test_default_service_name(self):
        """Test that default service name is used when not specified."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'

        mock_azure_monitor = MagicMock()
        mock_configure = MagicMock()
        mock_azure_monitor.configure_azure_monitor = mock_configure

        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry': MagicMock(),
            'opentelemetry.trace': MagicMock()
        }):
            from python.tracing_setup import configure_tracing

            configure_tracing()
            
            call_args = mock_configure.call_args
            resource_attrs = call_args.kwargs.get('resource_attributes', {})
            self.assertEqual(
                resource_attrs.get('service.name'),
                'abaco-loans-analytics',
                "Should use default service name"
            )

    def test_live_metrics_enabled(self):
        """Test that live metrics are enabled in configuration."""
        os.environ['APPLICATIONINSIGHTS_CONNECTION_STRING'] = 'InstrumentationKey=test-key;IngestionEndpoint=https://test.com'

        mock_azure_monitor = MagicMock()
        mock_configure = MagicMock()
        mock_azure_monitor.configure_azure_monitor = mock_configure

        with patch.dict('sys.modules', {
            'azure.monitor.opentelemetry': mock_azure_monitor,
            'opentelemetry': MagicMock(),
            'opentelemetry.trace': MagicMock()
        }):
            from python.tracing_setup import configure_tracing

            configure_tracing()
            
            call_args = mock_configure.call_args
            self.assertTrue(
                call_args.kwargs.get('enable_live_metrics', False),
                "Live metrics should be enabled"
            )


if __name__ == '__main__':
    unittest.main()
