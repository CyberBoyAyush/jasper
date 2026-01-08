"""
Structured error types for Jasper with user-friendly messages.
"""


class JasperError(Exception):
    """Base error for all Jasper exceptions."""
    def __init__(self, message: str, suggestion: str = None, debug_details: str = None):
        self.message = message
        self.suggestion = suggestion
        self.debug_details = debug_details
        super().__init__(self.message)


class ConfigError(JasperError):
    """Configuration or setup error (missing API keys, etc.)."""
    pass


class LLMError(JasperError):
    """LLM service unavailable or request failed."""
    pass


class DataProviderError(JasperError):
    """Financial data provider error."""
    pass


class ValidationError(JasperError):
    """Data validation error blocking synthesis."""
    pass


class QueryError(JasperError):
    """User query cannot be understood or processed."""
    pass
