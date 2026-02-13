"""
Task service layer with create_task and get_user_tasks functions.

[Task]: T045
[From]: specs/001-fullstack-web-app/plan.md, data-model.md
"""

from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from typing import List, Optional
from app.models.task import Task
from app.schemas.task import CreateTaskRequest, UpdateTaskRequest


def create_task(
    session: Session,
    user_id: UUID,
    request: CreateTaskRequest
) -> Task:
    """
    Create a new task for the authenticated user.

    [Task]: T045

    Args:
        session: Database session
        user_id: Authenticated user's ID
        request: Task creation request with title and optional description

    Returns:
        Created Task instance
    """
    new_task = Task(
        user_id=user_id,
        title=request.title,
        description=request.description,
        is_complete=False
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


def get_user_tasks(
    session: Session,
    user_id: UUID
) -> List[Task]:
    """
    Retrieve all tasks for a specific user, sorted by created_at DESC.

    [Task]: T045

    Args:
        session: Database session
        user_id: User ID to filter tasks

    Returns:
        List of Task instances sorted by creation date (newest first)
    """
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
    )

    tasks = session.exec(statement).all()
    return list(tasks)


def get_task_by_id(
    session: Session,
    task_id: UUID,
    user_id: UUID
) -> Optional[Task]:
    """
    Retrieve a single task by ID with ownership verification.

    [Task]: T045

    Args:
        session: Database session
        task_id: Task ID to retrieve
        user_id: User ID for ownership verification

    Returns:
        Task instance if found and owned by user, None otherwise
    """
    statement = (
        select(Task)
        .where(Task.id == task_id)
        .where(Task.user_id == user_id)
    )

    task = session.exec(statement).first()
    return task


def update_task(
    session: Session,
    task: Task,
    request: UpdateTaskRequest
) -> Task:
    """
    Update an existing task's title and description.

    [Task]: T081

    Args:
        session: Database session
        task: Task instance to update
        request: Update request with new title and description

    Returns:
        Updated Task instance
    """
    task.title = request.title
    task.description = request.description
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def toggle_task_completion(
    session: Session,
    task: Task,
    is_complete: bool
) -> Task:
    """
    Toggle task completion status.

    [Task]: T067, T068

    Args:
        session: Database session
        task: Task instance to update
        is_complete: New completion status

    Returns:
        Updated Task instance
    """
    task.is_complete = is_complete
    task.updated_at = datetime.utcnow()

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


def delete_task(
    session: Session,
    task: Task
) -> None:
    """
    Permanently delete a task.

    [Task]: T097

    Args:
        session: Database session
        task: Task instance to delete
    """
    session.delete(task)
    session.commit()
