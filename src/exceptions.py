from typing import Any

class CheckvistError(Exception):
    """Base exception for all Checkvist-related errors."""
    pass

class CheckvistAPIError(CheckvistError):
    """Raised when the API returns an error status code."""
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(f"{message} (Status: {status_code})" if status_code else message)

class CheckvistAuthError(CheckvistAPIError):
    """Raised when authentication fails (401/403)."""
    pass

class CheckvistRateLimitError(CheckvistAPIError):
    """Raised when the API rate limit is exceeded (429)."""
    pass

class CheckvistResourceNotFoundError(CheckvistAPIError):
    """Raised when a requested resource is not found (404)."""
    pass

class CheckvistConnectionError(CheckvistError):
    """Raised when the client cannot connect to the server."""
    pass

class CheckvistPartialSuccessError(CheckvistError):
    """Raised when a multi-step operation partially succeeds."""
    def __init__(self, message: str, partial_data: Any = None):
        self.partial_data = partial_data
        super().__init__(message)
