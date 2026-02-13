"""
Pydantic schemas for task requests and responses.

[Task]: T044, T046
[From]: specs/001-fullstack-web-app/contracts/openapi.yaml
"""

from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class CreateTaskRequest(BaseModel):
    """Request schema for creating a new task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional task description (max 1000 characters)"
    )

    @field_validator('title')
    @classmethod
    def validate_title_not_whitespace(cls, v: str) -> str:
        """Ensure title is not only whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip()

    @field_validator('description')
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Trim description if provided."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and vegetables"
            }
        }
    }


class UpdateTaskRequest(BaseModel):
    """Request schema for updating a task."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Task title (1-200 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional task description (max 1000 characters)"
    )

    @field_validator('title')
    @classmethod
    def validate_title_not_whitespace(cls, v: str) -> str:
        """Ensure title is not only whitespace."""
        if not v or not v.strip():
            raise ValueError('Title cannot be empty or only whitespace')
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries and cook dinner",
                "description": "Updated shopping list with dinner ingredients"
            }
        }
    }


class ToggleCompleteRequest(BaseModel):
    """Request schema for toggling task completion status."""

    is_complete: bool = Field(..., description="New completion status")

    model_config = {
        "json_schema_extra": {
            "example": {
                "is_complete": True
            }
        }
    }


class TaskResponse(BaseModel):
    """Response schema for a single task."""

    id: UUID = Field(..., description="Task unique identifier")
    user_id: UUID = Field(..., description="Owner user ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    is_complete: bool = Field(..., description="Completion status")
    created_at: datetime = Field(..., description="Creation timestamp (UTC)")
    updated_at: datetime = Field(..., description="Last update timestamp (UTC)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Buy groceries",
                "description": "Milk, eggs, bread, and vegetables",
                "is_complete": False,
                "created_at": "2026-01-15T10:35:00Z",
                "updated_at": "2026-01-15T10:35:00Z"
            }
        }
    }


class TaskListResponse(BaseModel):
    """Response schema for a list of tasks."""

    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    count: int = Field(..., description="Total number of tasks")

    model_config = {
        "json_schema_extra": {
            "example": {
                "tasks": [
                    {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "user_id": "550e8400-e29b-41d4-a716-446655440000",
                        "title": "Buy groceries",
                        "description": "Milk, eggs, bread",
                        "is_complete": False,
                        "created_at": "2026-01-15T10:35:00Z",
                        "updated_at": "2026-01-15T10:35:00Z"
                    }
                ],
                "count": 1
            }
        }
    }
