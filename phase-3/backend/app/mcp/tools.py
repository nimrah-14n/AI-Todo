"""
MCP Tools implementation for todo task management.

This module implements the actual tool functions that are called by the MCP server.
Each tool interacts with the database to perform CRUD operations on tasks.
"""
from typing import Any, Optional
from uuid import UUID, uuid4
from sqlmodel import Session, select
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

logger = logging.getLogger(__name__)


class TodoTools:
    """Collection of MCP tools for todo task management."""

    def __init__(self, session: Session, user_id: UUID):
        """
        Initialize tools with database session and user context.

        Args:
            session: SQLModel database session
            user_id: UUID of the authenticated user
        """
        self.session = session
        self.user_id = user_id

    async def add_task(self, title: str, description: Optional[str] = None) -> dict[str, Any]:
        """
        Create a new todo task.

        Args:
            title: Task title (1-200 characters)
            description: Optional task description (max 1000 characters)

        Returns:
            Dictionary with task_id and confirmation message

        Raises:
            ValueError: If title is invalid or database operation fails
        """
        # Import here to avoid circular dependency
        from ..models.task import Task

        try:
            # Validate title
            if not title or len(title.strip()) == 0:
                logger.warning(f"Attempted to create task with empty title for user {self.user_id}")
                raise ValueError("Task title cannot be empty")
            if len(title) > 200:
                logger.warning(f"Attempted to create task with title too long ({len(title)} chars) for user {self.user_id}")
                raise ValueError("Task title must be 200 characters or less")

            # Validate description if provided
            if description and len(description) > 1000:
                logger.warning(f"Attempted to create task with description too long ({len(description)} chars) for user {self.user_id}")
                raise ValueError("Task description must be 1000 characters or less")

            # Create task
            task = Task(
                user_id=self.user_id,
                title=title.strip(),
                description=description.strip() if description else None,
                is_complete=False
            )

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Created task {task.id} for user {self.user_id}: '{task.title}'")

            return {
                "task_id": str(task.id),
                "title": task.title,
                "message": f"Task '{task.title}' created successfully"
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Database integrity error creating task for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to create task: database constraint violation")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error creating task for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to create task: database error occurred")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error creating task for user {self.user_id}: {str(e)}")
            raise ValueError(f"Failed to create task: {str(e)}")

    async def list_tasks(self, is_complete: Optional[bool] = None) -> dict[str, Any]:
        """
        List all tasks for the user.

        Args:
            is_complete: Optional filter by completion status

        Returns:
            Dictionary with list of tasks

        Raises:
            ValueError: If database operation fails
        """
        # Import here to avoid circular dependency
        from ..models.task import Task

        try:
            # Build query
            query = select(Task).where(Task.user_id == self.user_id)

            if is_complete is not None:
                query = query.where(Task.is_complete == is_complete)

            # Order by created_at descending (newest first)
            query = query.order_by(Task.created_at.desc())

            # Execute query
            tasks = self.session.exec(query).all()

            # Format response
            task_list = [
                {
                    "task_id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "is_complete": task.is_complete,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]

            logger.info(f"Listed {len(task_list)} tasks for user {self.user_id} (is_complete={is_complete})")

            return {
                "tasks": task_list,
                "count": len(task_list)
            }

        except SQLAlchemyError as e:
            logger.error(f"Database error listing tasks for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to list tasks: database error occurred")
        except Exception as e:
            logger.error(f"Unexpected error listing tasks for user {self.user_id}: {str(e)}")
            raise ValueError(f"Failed to list tasks: {str(e)}")

    async def complete_task(self, task_id: str) -> dict[str, Any]:
        """
        Mark a task as complete.

        Args:
            task_id: UUID of the task to complete

        Returns:
            Dictionary with confirmation message

        Raises:
            ValueError: If task_id is invalid, task not found, or database operation fails
        """
        # Import here to avoid circular dependency
        from ..models.task import Task

        try:
            # Parse UUID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                logger.warning(f"Invalid task_id format attempted: {task_id} for user {self.user_id}")
                raise ValueError(f"Invalid task_id format: {task_id}")

            # Find task
            task = self.session.get(Task, task_uuid)

            if not task:
                logger.warning(f"Task not found: {task_id} for user {self.user_id}")
                raise ValueError(f"Task not found: {task_id}")

            if task.user_id != self.user_id:
                logger.warning(f"User {self.user_id} attempted to access task {task_id} belonging to user {task.user_id}")
                raise ValueError(f"Task {task_id} does not belong to user")

            # Check if already complete
            if task.is_complete:
                logger.info(f"Task {task_id} already complete for user {self.user_id}")
                return {
                    "task_id": str(task.id),
                    "title": task.title,
                    "message": f"Task '{task.title}' is already complete"
                }

            # Mark as complete
            task.is_complete = True
            task.updated_at = datetime.utcnow()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Completed task {task.id} for user {self.user_id}: '{task.title}'")

            return {
                "task_id": str(task.id),
                "title": task.title,
                "message": f"Task '{task.title}' marked as complete"
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Database integrity error completing task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to complete task: database constraint violation")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error completing task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to complete task: database error occurred")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error completing task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError(f"Failed to complete task: {str(e)}")

    async def delete_task(self, task_id: str) -> dict[str, Any]:
        """
        Delete a task.

        Args:
            task_id: UUID of the task to delete

        Returns:
            Dictionary with confirmation message

        Raises:
            ValueError: If task_id is invalid, task not found, or database operation fails
        """
        # Import here to avoid circular dependency
        from ..models.task import Task

        try:
            # Parse UUID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                logger.warning(f"Invalid task_id format attempted: {task_id} for user {self.user_id}")
                raise ValueError(f"Invalid task_id format: {task_id}")

            # Find task
            task = self.session.get(Task, task_uuid)

            if not task:
                logger.warning(f"Task not found: {task_id} for user {self.user_id}")
                raise ValueError(f"Task not found: {task_id}")

            if task.user_id != self.user_id:
                logger.warning(f"User {self.user_id} attempted to delete task {task_id} belonging to user {task.user_id}")
                raise ValueError(f"Task {task_id} does not belong to user")

            # Store title for confirmation message
            task_title = task.title

            # Delete task
            self.session.delete(task)
            self.session.commit()

            logger.info(f"Deleted task {task_id} for user {self.user_id}: '{task_title}'")

            return {
                "task_id": task_id,
                "message": f"Task '{task_title}' deleted successfully"
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Database integrity error deleting task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to delete task: database constraint violation")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error deleting task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to delete task: database error occurred")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error deleting task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError(f"Failed to delete task: {str(e)}")

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Update a task's title or description.

        Args:
            task_id: UUID of the task to update
            title: New task title (1-200 characters)
            description: New task description (max 1000 characters)

        Returns:
            Dictionary with confirmation message

        Raises:
            ValueError: If task_id is invalid, task not found, validation fails, or database operation fails
        """
        # Import here to avoid circular dependency
        from ..models.task import Task

        try:
            # Parse UUID
            try:
                task_uuid = UUID(task_id)
            except ValueError:
                logger.warning(f"Invalid task_id format attempted: {task_id} for user {self.user_id}")
                raise ValueError(f"Invalid task_id format: {task_id}")

            # Find task
            task = self.session.get(Task, task_uuid)

            if not task:
                logger.warning(f"Task not found: {task_id} for user {self.user_id}")
                raise ValueError(f"Task not found: {task_id}")

            if task.user_id != self.user_id:
                logger.warning(f"User {self.user_id} attempted to update task {task_id} belonging to user {task.user_id}")
                raise ValueError(f"Task {task_id} does not belong to user")

            # Check if at least one field is provided
            if title is None and description is None:
                logger.warning(f"Update task called with no fields to update for task {task_id}")
                raise ValueError("At least one field (title or description) must be provided for update")

            # Update title if provided
            if title is not None:
                if not title or len(title.strip()) == 0:
                    logger.warning(f"Attempted to update task {task_id} with empty title for user {self.user_id}")
                    raise ValueError("Task title cannot be empty")
                if len(title) > 200:
                    logger.warning(f"Attempted to update task {task_id} with title too long ({len(title)} chars) for user {self.user_id}")
                    raise ValueError("Task title must be 200 characters or less")
                task.title = title.strip()

            # Update description if provided
            if description is not None:
                if len(description) > 1000:
                    logger.warning(f"Attempted to update task {task_id} with description too long ({len(description)} chars) for user {self.user_id}")
                    raise ValueError("Task description must be 1000 characters or less")
                task.description = description.strip() if description else None

            # Update timestamp
            task.updated_at = datetime.utcnow()

            self.session.add(task)
            self.session.commit()
            self.session.refresh(task)

            logger.info(f"Updated task {task.id} for user {self.user_id}: '{task.title}'")

            return {
                "task_id": str(task.id),
                "title": task.title,
                "description": task.description,
                "message": f"Task '{task.title}' updated successfully"
            }

        except ValueError:
            # Re-raise validation errors
            raise
        except IntegrityError as e:
            self.session.rollback()
            logger.error(f"Database integrity error updating task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to update task: database constraint violation")
        except SQLAlchemyError as e:
            self.session.rollback()
            logger.error(f"Database error updating task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError("Failed to update task: database error occurred")
        except Exception as e:
            self.session.rollback()
            logger.error(f"Unexpected error updating task {task_id} for user {self.user_id}: {str(e)}")
            raise ValueError(f"Failed to update task: {str(e)}")
