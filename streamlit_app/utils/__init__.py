"""Adapter utils package - re-exports from dashboard.utils with lazy loading.

This module provides backward compatibility for imports like:
    from streamlit_app.utils import DataIngestionEngine, FeatureEngineer
    from streamlit_app.utils.business_rules import BUSINESS_RULES
"""

from dashboard.utils import (
    available_utils,
    FeatureEngineer,
)

__all__ = ["available_utils", "FeatureEngineer"]
