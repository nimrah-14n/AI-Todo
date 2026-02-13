"""
Task routes for CRUD operations.

[Task]: T041, T042, T043, T065, T079, T096
[From]: specs/001-fullstack-web-app/contracts/openapi.yaml
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from uuid import UUID
from typing import List
from app.database import get_session
from app.dependencies.auth import get_current_user_id, verify_user_access
from app.schemas.task import (
    CreateTaskRequest,
    UpdateTaskRequest,
    ToggleCompleteRequest,
    TaskResponse,
    TaskListResponse
)
from app.services import task as task_service

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: UUID,
    request: CreateTaskRequest,
    session: Session = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Create a new task for the authenticated user.

    [Task]: T041

    Args:
        user_id: User ID from URL path
        request: Task creation request
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        Created task

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Verify user can only create tasks for themselves
    await verify_user_access(current_user_id, user_id)

    # Create task
    task = task_service.create_task(session, user_id, request)

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_complete=task.is_complete,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    user_id: UUID,
    session: Session = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Retrieve all tasks for the authenticated user.

    [Task]: T042

    Args:
        user_id: User ID from URL path
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        List of tasks sorted by created_at DESC

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
    """
    # Verify user can only access their own tasks
    await verify_user_access(current_user_id, user_id)

    # Get tasks
    tasks = task_service.get_user_tasks(session, user_id)

    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                title=task.title,
                description=task.description,
                is_complete=task.is_complete,
                created_at=task.created_at,
                updated_at=task.updated_at
            )
            for task in tasks
        ],
        count=len(tasks)
    )


@router.get("/{id}", response_model=TaskResponse)
async def get_task(
    user_id: UUID,
    id: UUID,
    session: Session = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Retrieve a single task by ID.

    [Task]: T043

    Args:
        user_id: User ID from URL path
        id: Task ID
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        Task details

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Verify user can only access their own tasks
    await verify_user_access(current_user_id, user_id)

    # Get task
    task = task_service.get_task_by_id(session, id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        title=task.title,
        description=task.description,
        is_complete=task.is_complete,
        created_at=task.created_at,
        updated_at=task.updated_at
    )


@router.patch("/{id}/complete", response_model=TaskResponse)
async def toggle_task_complete(
    user_id: UUID,
    id: UUID,
    request: ToggleCompleteRequest,
    session: Session = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Toggle task completion status.

    [Task]: T065

    Args:
        user_id: User ID from URL path
        id: Task ID
        request: Toggle completion request
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        Updated task

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Verify user can only modify their own tasks
    await verify_user_access(current_user_id, user_id)

    # Get task
    task = task_service.get_task_by_id(session, id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Toggle completion
    updated_task = task_service.toggle_task_completion(
        session, task, request.is_complete
    )

    return TaskResponse(
        id=updated_task.id,
        user_id=updated_task.user_id,
        title=updated_task.title,
        description=updated_task.description,
        is_complete=updated_task.is_complete,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at
    )


@router.put("/{id}", response_model=TaskResponse)
async def update_task(
    user_id: UUID,
    id: UUID,
    request: UpdateTaskRequest,
    session: Session = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Update task title and description.

    [Task]: T079

    Args:
        user_id: User ID from URL path
        id: Task ID
        request: Update request
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Returns:
        Updated task

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Verify user can only modify their own tasks
    await verify_user_access(current_user_id, user_id)

    # Get task
    task = task_service.get_task_by_id(session, id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update task
    updated_task = task_service.update_task(session, task, request)

    return TaskResponse(
        id=updated_task.id,
        user_id=updated_task.user_id,
        title=updated_task.title,
        description=updated_task.description,
        is_complete=updated_task.is_complete,
        created_at=updated_task.created_at,
        updated_at=updated_task.updated_at
    )


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: UUID,
    id: UUID,
    session: Session = Depends(get_session),
    current_user_id: UUID = Depends(get_current_user_id)
):
    """
    Permanently delete a task.

    [Task]: T096

    Args:
        user_id: User ID from URL path
        id: Task ID
        session: Database session
        current_user_id: Authenticated user ID from JWT

    Raises:
        HTTPException: 403 if user_id doesn't match authenticated user
        HTTPException: 404 if task not found
    """
    # Verify user can only delete their own tasks
    await verify_user_access(current_user_id, user_id)

    # Get task
    task = task_service.get_task_by_id(session, id, user_id)

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Delete task
    task_service.delete_task(session, task)

    return None
