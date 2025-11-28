"""Utility exports for Streamlit features with lazy loading."""

from typing import TYPE_CHECKING, Any

__all__ = ["FeatureEngineer"]

if TYPE_CHECKING:  # pragma: no cover - used for type checkers only
    from .feature_engineering import FeatureEngineer


def __getattr__(name: str) -> Any:
    """Lazily import heavy dependencies when requested."""
    if name == "FeatureEngineer":
        from .feature_engineering import FeatureEngineer as _FeatureEngineer

        globals()[name] = _FeatureEngineer
        return _FeatureEngineer
    raise AttributeError(f"module 'streamlit_app.utils' has no attribute {name!r}")
