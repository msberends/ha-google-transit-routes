"""Exceptions for the Google Transit Routes integration."""


class GoogleRoutesApiError(Exception):
    """Base exception for the Google Routes API client."""


class InvalidRequest(GoogleRoutesApiError):
    """Raised when the API rejects the request as malformed (HTTP 400)."""


class InvalidApiKey(GoogleRoutesApiError):
    """Raised when the API key is invalid or lacks permission (HTTP 403)."""


class RateLimited(GoogleRoutesApiError):
    """Raised when the API quota has been exceeded (HTTP 429)."""


class ApiUnavailable(GoogleRoutesApiError):
    """Raised when the API is unavailable (HTTP 5xx)."""
