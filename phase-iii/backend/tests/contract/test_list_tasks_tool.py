"""
Contract tests for list_tasks MCP tool.
RED PHASE: These tests should FAIL until the tool is properly implemented

Contract tests verify that the tool adheres to its input/output schema
and handles filtering correctly.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from src.mcp.tools import TodoTools
from src.models.user import User
from src.models.task import Task


@pytest.fixture
def engine():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Create database session"""
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_user(session):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password="hashed_password_here"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def todo_tools(session, test_user):
    """Create TodoTools instance"""
    return TodoTools(session=session, user_id=test_user.id)


@pytest.fixture
def sample_tasks(session, test_user):
    """Create sample tasks for testing"""
    tasks = [
        Task(user_id=test_user.id, title="Buy groceries", is_complete=False),
        Task(user_id=test_user.id, title="Call mom", is_complete=True),
        Task(user_id=test_user.id, title="Finish report", is_complete=False),
        Task(user_id=test_user.id, title="Clean house", is_complete=True),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


@pytest.mark.asyncio
async def test_list_tasks_output_schema(todo_tools, sample_tasks):
    """Test that list_tasks returns correct output schema"""
    result = await todo_tools.list_tasks()

    # Output must contain these fields
    assert "tasks" in result
    assert "count" in result

    # tasks must be a list
    assert isinstance(result["tasks"], list)

    # count must match list length
    assert result["count"] == len(result["tasks"])

    # Each task must have required fields
    for task in result["tasks"]:
        assert "task_id" in task
        assert "title" in task
        assert "description" in task
        assert "is_complete" in task
        assert "created_at" in task


@pytest.mark.asyncio
async def test_list_tasks_returns_all_tasks(todo_tools, sample_tasks):
    """Test that list_tasks returns all user's tasks by default"""
    result = await todo_tools.list_tasks()

    assert result["count"] == 4
    assert len(result["tasks"]) == 4


@pytest.mark.asyncio
async def test_list_tasks_filter_incomplete(todo_tools, sample_tasks):
    """Test filtering for incomplete tasks only"""
    result = await todo_tools.list_tasks(is_complete=False)

    assert result["count"] == 2
    assert len(result["tasks"]) == 2

    # All returned tasks should be incomplete
    for task in result["tasks"]:
        assert task["is_complete"] is False


@pytest.mark.asyncio
async def test_list_tasks_filter_complete(todo_tools, sample_tasks):
    """Test filtering for complete tasks only"""
    result = await todo_tools.list_tasks(is_complete=True)

    assert result["count"] == 2
    assert len(result["tasks"]) == 2

    # All returned tasks should be complete
    for task in result["tasks"]:
        assert task["is_complete"] is True


@pytest.mark.asyncio
async def test_list_tasks_empty_list(todo_tools):
    """Test that list_tasks handles empty task list"""
    result = await todo_tools.list_tasks()

    assert result["count"] == 0
    assert result["tasks"] == []


@pytest.mark.asyncio
async def test_list_tasks_ordered_by_created_at(todo_tools, session, test_user):
    """Test that tasks are ordered by created_at descending (newest first)"""
    import time

    # Create tasks with slight time delays
    task1 = Task(user_id=test_user.id, title="First task")
    session.add(task1)
    session.commit()

    time.sleep(0.01)

    task2 = Task(user_id=test_user.id, title="Second task")
    session.add(task2)
    session.commit()

    time.sleep(0.01)

    task3 = Task(user_id=test_user.id, title="Third task")
    session.add(task3)
    session.commit()

    result = await todo_tools.list_tasks()

    # Should be ordered newest first
    assert result["tasks"][0]["title"] == "Third task"
    assert result["tasks"][1]["title"] == "Second task"
    assert result["tasks"][2]["title"] == "First task"


@pytest.mark.asyncio
async def test_list_tasks_only_returns_user_tasks(session, sample_tasks):
    """Test that list_tasks only returns tasks for the specific user"""
    # Create another user with tasks
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_password_here"
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    other_task = Task(user_id=other_user.id, title="Other user's task")
    session.add(other_task)
    session.commit()

    # Get first user's tools
    first_user_id = sample_tasks[0].user_id
    tools = TodoTools(session=session, user_id=first_user_id)

    result = await tools.list_tasks()

    # Should only return first user's tasks (4 tasks)
    assert result["count"] == 4

    # Verify none of the tasks belong to other user
    for task in result["tasks"]:
        assert task["task_id"] != str(other_task.id)


@pytest.mark.asyncio
async def test_list_tasks_includes_description(todo_tools, session, test_user):
    """Test that list_tasks includes task descriptions"""
    task = Task(
        user_id=test_user.id,
        title="Task with description",
        description="This is a detailed description"
    )
    session.add(task)
    session.commit()

    result = await todo_tools.list_tasks()

    assert result["count"] == 1
    assert result["tasks"][0]["description"] == "This is a detailed description"


@pytest.mark.asyncio
async def test_list_tasks_null_description(todo_tools, session, test_user):
    """Test that list_tasks handles null descriptions"""
    task = Task(
        user_id=test_user.id,
        title="Task without description",
        description=None
    )
    session.add(task)
    session.commit()

    result = await todo_tools.list_tasks()

    assert result["count"] == 1
    assert result["tasks"][0]["description"] is None


@pytest.mark.asyncio
async def test_list_tasks_task_id_format(todo_tools, sample_tasks):
    """Test that task_id is returned as string UUID"""
    result = await todo_tools.list_tasks()

    for task in result["tasks"]:
        # Should be a string
        assert isinstance(task["task_id"], str)

        # Should be valid UUID format
        from uuid import UUID
        try:
            UUID(task["task_id"])
        except ValueError:
            pytest.fail(f"task_id '{task['task_id']}' is not a valid UUID")


@pytest.mark.asyncio
async def test_list_tasks_created_at_format(todo_tools, sample_tasks):
    """Test that created_at is returned as ISO format string"""
    result = await todo_tools.list_tasks()

    for task in result["tasks"]:
        # Should be a string
        assert isinstance(task["created_at"], str)

        # Should be valid ISO format
        from datetime import datetime
        try:
            datetime.fromisoformat(task["created_at"])
        except ValueError:
            pytest.fail(f"created_at '{task['created_at']}' is not valid ISO format")
