"""
Custom exceptions for Jasper's data provider layer.
Prefer using core.errors.DataProviderError instead.
"""

from ..core.errors import DataProviderError

# Keep for backward compatibility
__all__ = ["DataProviderError"]
