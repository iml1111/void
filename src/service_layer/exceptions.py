"""Service Layer Exceptions

Define business logic exceptions that can be raised by services.
These exceptions are independent of infrastructure (HTTP, database, etc.).
"""


class ServiceError(Exception):
    """
    Base exception for all service layer errors

    All service-specific exceptions should inherit from this class.
    This allows catch-all handling at the entrypoint layer.

    Attributes:
        status_code: HTTP status code for API response
        error_type: Error type label for API response
    """

    status_code: int = 500
    error_type: str = "Service Error"


class ItemNotFoundError(ServiceError):
    """Item with given ID does not exist"""

    status_code = 404
    error_type = "Not Found"


class ItemValidationError(ServiceError):
    """Item data validation failed"""

    status_code = 400
    error_type = "Validation Error"


class ExternalAPIError(ServiceError):
    """
    External API call failed

    Base exception for all external service integration errors.
    Subclass for specific API failures.
    """

    status_code = 502
    error_type = "External API Error"


class AuthenticationError(ServiceError):
    """Base exception for authentication errors"""

    status_code = 401
    error_type = "Authentication Error"


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password"""

    status_code = 401
    error_type = "Invalid Credentials"


class SessionExpiredError(AuthenticationError):
    """Session has expired or does not exist"""

    status_code = 401
    error_type = "Session Expired"


class InvalidTokenError(AuthenticationError):
    """Invalid or malformed token"""

    status_code = 401
    error_type = "Invalid Token"
