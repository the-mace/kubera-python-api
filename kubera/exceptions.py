"""Kubera API exceptions."""


class KuberaAPIError(Exception):
    """Base exception for all Kubera API errors."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
        """
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class KuberaAuthenticationError(KuberaAPIError):
    """Raised when authentication fails."""

    pass


class KuberaRateLimitError(KuberaAPIError):
    """Raised when rate limit is exceeded."""

    pass


class KuberaValidationError(KuberaAPIError):
    """Raised when request validation fails."""

    pass
