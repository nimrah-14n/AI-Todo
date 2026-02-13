"""
Global error handler middleware for consistent API error responses.

[Task]: T109
[From]: specs/001-fullstack-web-app/plan.md
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors with consistent format.
    """
    errors = exc.errors()

    # Get first error for simplicity
    if errors:
        first_error = errors[0]
        field = ".".join(str(loc) for loc in first_error["loc"] if loc != "body")
        message = first_error["msg"]

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation failed",
                "field": field if field else None,
                "details": message
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation failed",
            "field": None,
            "details": "Invalid request data"
        }
    )


async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity errors (e.g., unique constraint violations).
    """
    error_message = str(exc.orig) if hasattr(exc, 'orig') else str(exc)

    # Check for common integrity errors
    if "unique constraint" in error_message.lower() or "duplicate" in error_message.lower():
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Duplicate entry",
                "field": None,
                "details": "This record already exists"
            }
        )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Database constraint violation",
            "field": None,
            "details": "The operation violates database constraints"
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected errors with generic error response.
    """
    # Log the error (in production, use proper logging)
    print(f"Unexpected error: {type(exc).__name__}: {str(exc)}")

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "field": None,
            "details": "An unexpected error occurred. Please try again later."
        }
    )
