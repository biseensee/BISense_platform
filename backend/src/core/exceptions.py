"""Domain/application exception hierarchy and their HTTP mapping.

Domain and application layers raise these exceptions and know nothing about
HTTP. The presentation layer (see `core/error_handlers.py`) is the only place
that translates them into `HTTPException` / JSON responses — this keeps the
inner layers framework-agnostic per Clean Architecture.
"""
from __future__ import annotations


class DomainError(Exception):
    """Base class for all business-rule violations."""

    code = "domain_error"
    http_status = 400

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}


class EntityNotFoundError(DomainError):
    code = "not_found"
    http_status = 404

    def __init__(self, entity: str, identifier: object) -> None:
        super().__init__(f"{entity} with id={identifier!r} was not found")


class EntityAlreadyExistsError(DomainError):
    code = "already_exists"
    http_status = 409


class ValidationError(DomainError):
    code = "validation_error"
    http_status = 422


class AuthenticationError(DomainError):
    code = "authentication_error"
    http_status = 401


class AuthorizationError(DomainError):
    code = "authorization_error"
    http_status = 403


class RateLimitedError(DomainError):
    code = "rate_limited"
    http_status = 429


class DataSourceConnectionError(DomainError):
    code = "datasource_connection_error"
    http_status = 502


class QueryExecutionError(DomainError):
    code = "query_execution_error"
    http_status = 400
