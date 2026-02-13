"""
Error response schemas for consistent API error handling.

[Task]: T110
[From]: specs/001-fullstack-web-app/plan.md
"""

from pydantic import BaseModel, Field
from typing import Optional


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    error: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Field that caused the error (if applicable)")
    details: Optional[str] = Field(None, description="Additional error details")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Validation failed",
                "field": "email",
                "details": "Email address is already registered"
            }
        }
    }
