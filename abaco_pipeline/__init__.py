"""Compatibility shim for running the v2 pipeline as a top-level module."""

from python.abaco_pipeline import __version__

__all__ = ["__version__"]
