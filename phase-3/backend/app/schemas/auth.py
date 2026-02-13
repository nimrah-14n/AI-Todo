"""
Pydantic schemas for authentication requests and responses.

[Task]: T024
[From]: specs/001-fullstack-web-app/contracts/openapi.yaml
"""

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime


class SignupRequest(BaseModel):
    """Request schema for user signup."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "alice@example.com",
                "password": "securepass123"
            }
        }
    }


class SigninRequest(BaseModel):
    """Request schema for user signin."""

    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "alice@example.com",
                "password": "securepass123"
            }
        }
    }


class UserResponse(BaseModel):
    """User information in authentication responses."""

    id: UUID = Field(..., description="User's unique identifier")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp (UTC)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "alice@example.com",
                "created_at": "2026-01-15T10:30:00Z"
            }
        }
    }


class AuthResponse(BaseModel):
    """Response schema for successful authentication."""

    token: str = Field(..., description="JWT authentication token")
    user: UserResponse = Field(..., description="User information")

    model_config = {
        "json_schema_extra": {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "alice@example.com",
                    "created_at": "2026-01-15T10:30:00Z"
                }
            }
        }
    }
