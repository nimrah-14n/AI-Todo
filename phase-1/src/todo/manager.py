"""TaskManager - Manages todo tasks in memory."""

from typing import Optional

from .exceptions import (
    DescriptionTooLongError,
    EmptyTitleError,
    TaskNotFoundError,
    TitleTooLongError,
)
from .models import Task

MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000


def validate_title(title: str) -> None:
    """Validate task title."""
    if not title or not title.strip():
        raise EmptyTitleError()
    if len(title) > MAX_TITLE_LENGTH:
        raise TitleTooLongError(len(title))


def validate_description(description: str) -> None:
    """Validate task description."""
    if len(description) > MAX_DESCRIPTION_LENGTH:
        raise DescriptionTooLongError(len(description))


class TaskManager:
    """Manages a collection of tasks in memory."""

    def __init__(self):
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def _generate_id(self) -> int:
        """Generate a unique sequential ID."""
        current_id = self._next_id
        self._next_id += 1
        return current_id

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task with title and optional description."""
        validate_title(title)
        validate_description(description)

        task = Task(
            id=self._generate_id(),
            title=title.strip(),
            description=description.strip() if description else "",
        )
        self._tasks[task.id] = task
        return task

    def get_task(self, task_id: int) -> Task:
        """Get a task by ID."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks sorted by ID."""
        return [self._tasks[task_id] for task_id in sorted(self._tasks.keys())]

    def get_pending_tasks(self) -> list[Task]:
        """Get all pending (incomplete) tasks sorted by ID."""
        return [
            self._tasks[task_id]
            for task_id in sorted(self._tasks.keys())
            if not self._tasks[task_id].completed
        ]

    def get_completed_tasks(self) -> list[Task]:
        """Get all completed tasks sorted by ID."""
        return [
            self._tasks[task_id]
            for task_id in sorted(self._tasks.keys())
            if self._tasks[task_id].completed
        ]

    def task_count(self) -> dict[str, int]:
        """Get task counts by status."""
        total = len(self._tasks)
        completed = sum(1 for task in self._tasks.values() if task.completed)
        return {"total": total, "completed": completed, "pending": total - completed}

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle task completion status."""
        task = self.get_task(task_id)
        task.completed = not task.completed
        return task

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Task:
        """Update task title and/or description."""
        task = self.get_task(task_id)

        if title is not None:
            validate_title(title)
            task.title = title.strip()

        if description is not None:
            validate_description(description)
            task.description = description.strip() if description else ""

        return task

    def delete_task(self, task_id: int) -> None:
        """Delete a task by ID."""
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        del self._tasks[task_id]
