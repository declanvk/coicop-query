"""Custom exceptions for the coicop-query tool."""


class CoicopQueryError(Exception):
    """Base exception for coicop-query errors."""


class CategoryNotFoundError(CoicopQueryError):
    """Raised when a COICOP category is not found."""
