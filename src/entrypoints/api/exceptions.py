"""
Exception Handlers

Global exception handlers for the FastAPI application.
"""
import traceback
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from loguru import logger


def _serialize_body_for_json(body) -> str | dict | None:
    """
    Serialize request body for JSON response.

    RequestValidationError.body can be bytes, dict, or None.

    Args:
        body: Request body from RequestValidationError

    Returns:
        JSON-serializable representation of body
    """
    if body is None:
        return None
    if isinstance(body, bytes):
        try:
            return body.decode('utf-8')
        except UnicodeDecodeError:
            return '<binary data>'
    return body


def _serialize_validation_errors(errors: list) -> list:
    """
    Recursively serialize validation errors for JSON response.

    Args:
        errors: List of validation error dicts

    Returns:
        List of validation errors with bytes converted to strings
    """
    serialized = []
    for error in errors:
        error_copy = error.copy()
        if 'input' in error_copy and isinstance(error_copy['input'], bytes):
            try:
                error_copy['input'] = error_copy['input'].decode('utf-8')
            except UnicodeDecodeError:
                error_copy['input'] = '<binary data>'
        if 'ctx' in error_copy and isinstance(error_copy['ctx'], dict):
            for key, value in error_copy['ctx'].items():
                if isinstance(value, bytes):
                    try:
                        error_copy['ctx'][key] = value.decode('utf-8')
                    except UnicodeDecodeError:
                        error_copy['ctx'][key] = '<binary data>'
        serialized.append(error_copy)
    return serialized


def setup_exception_handlers(app: FastAPI) -> None:
    """
    Configure global exception handlers

    Args:
        app: FastAPI application instance
    """

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError
    ):
        """Handle validation errors"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation Error",
                "detail": _serialize_validation_errors(exc.errors()),
                "body": _serialize_body_for_json(
                    exc.body
                ) if hasattr(exc, 'body') else None,
            }
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle general exceptions"""
        # Log error with traceback
        tb_list = traceback.format_list(
            traceback.extract_tb(exc.__traceback__)
        )[-3:]
        tb_str = "".join(tb_list)
        tb_str += traceback.format_exception_only(type(exc), exc)[-1]

        logger.error(
            f"Unhandled exception: {exc}",
            extra={"traceback": tb_str, "url": str(request.url)}
        )

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred"
            }
        )
