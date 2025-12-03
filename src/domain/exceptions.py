"""Domain Exceptions

Pure Python domain exceptions without HTTP/infrastructure concerns.
These exceptions represent domain-level error conditions.
"""


class DomainError(Exception):
    """
    Base exception for all domain errors.

    All domain-specific exceptions should inherit from this class.
    This allows catch-all handling at upper layers while keeping
    the domain layer pure (no HTTP status codes or API concerns).
    """

    pass


# =============================================================================
# Entity-Related Exceptions
# =============================================================================


class EntityNotFoundError(DomainError):
    """Entity with given ID does not exist"""

    pass


class EntityValidationError(DomainError):
    """Entity data validation failed"""

    pass


# =============================================================================
# Item-Specific Exceptions
# =============================================================================


class ItemNotFoundError(EntityNotFoundError):
    """Item with given ID does not exist"""

    pass


class ItemValidationError(EntityValidationError):
    """Item data validation failed"""

    pass


# =============================================================================
# External Integration Exceptions
# =============================================================================


class ExternalServiceError(DomainError):
    """
    External service call failed.

    Base exception for all external service integration errors.
    Subclass for specific service failures.
    """

    pass


class ExternalAPIError(ExternalServiceError):
    """External API call failed"""

    pass


# =============================================================================
# Authentication Exceptions
# =============================================================================


class AuthenticationError(DomainError):
    """Base exception for authentication errors"""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Invalid username or password"""

    pass


class SessionExpiredError(AuthenticationError):
    """Session has expired or does not exist"""

    pass


class InvalidTokenError(AuthenticationError):
    """Invalid or malformed token"""

    pass
