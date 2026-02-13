"""
Contract tests for delete_task MCP tool.
RED PHASE: These tests should FAIL until the tool is properly implemented

Contract tests verify that the tool adheres to its input/output schema
and handles ownership validation correctly.
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
def sample_task(session, test_user):
    """Create a sample task"""
    task = Task(
        user_id=test_user.id,
        title="Buy groceries",
        is_complete=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.mark.asyncio
async def test_delete_task_output_schema(todo_tools, sample_task):
    """Test that delete_task returns correct output schema"""
    result = await todo_tools.delete_task(task_id=str(sample_task.id))

    # Output must contain these fields
    assert "task_id" in result
    assert "message" in result

    # task_id must match input
    assert result["task_id"] == str(sample_task.id)

    # message must be a non-empty string
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0


@pytest.mark.asyncio
async def test_delete_task_removes_from_database(todo_tools, sample_task, session):
    """Test that delete_task actually removes the task from database"""
    task_id = sample_task.id

    # Delete the task
    result = await todo_tools.delete_task(task_id=str(task_id))

    # Verify task no longer exists in database
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_task_invalid_uuid(todo_tools):
    """Test that delete_task rejects invalid UUID format"""
    with pytest.raises(ValueError, match="Invalid task_id format"):
        await todo_tools.delete_task(task_id="not-a-uuid")


@pytest.mark.asyncio
async def test_delete_task_nonexistent_task(todo_tools):
    """Test that delete_task rejects non-existent task"""
    fake_uuid = str(uuid4())

    with pytest.raises(ValueError, match="Task not found"):
        await todo_tools.delete_task(task_id=fake_uuid)


@pytest.mark.asyncio
async def test_delete_task_ownership_validation(session, sample_task):
    """Test that delete_task validates task ownership"""
    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_password_here"
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Try to delete task with wrong user
    other_tools = TodoTools(session=session, user_id=other_user.id)

    with pytest.raises(ValueError, match="does not belong to user"):
        await other_tools.delete_task(task_id=str(sample_task.id))

    # Verify task still exists
    task = session.get(Task, sample_task.id)
    assert task is not None


@pytest.mark.asyncio
async def test_delete_task_confirmation_message(todo_tools, sample_task):
    """Test that delete_task returns a helpful confirmation message"""
    result = await todo_tools.delete_task(task_id=str(sample_task.id))

    message = result["message"].lower()

    # Message should mention deletion
    assert any(word in message for word in ["delete", "removed", "deleted"])

    # Message should mention the task title
    assert sample_task.title.lower() in message or "task" in message


@pytest.mark.asyncio
async def test_delete_complete_task(todo_tools, session, test_user):
    """Test deleting a completed task"""
    task = Task(
        user_id=test_user.id,
        title="Completed task",
        is_complete=True
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    task_id = task.id

    # Should be able to delete completed tasks
    result = await todo_tools.delete_task(task_id=str(task_id))

    assert result is not None

    # Verify task is deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_task_with_description(todo_tools, session, test_user):
    """Test deleting a task that has a description"""
    task = Task(
        user_id=test_user.id,
        title="Task with description",
        description="Important details",
        is_complete=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    task_id = task.id

    # Should be able to delete tasks with descriptions
    result = await todo_tools.delete_task(task_id=str(task_id))

    assert result is not None

    # Verify task is deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


@pytest.mark.asyncio
async def test_delete_task_returns_task_id(todo_tools, sample_task):
    """Test that delete_task returns the deleted task's ID"""
    task_id = str(sample_task.id)

    result = await todo_tools.delete_task(task_id=task_id)

    assert result["task_id"] == task_id


@pytest.mark.asyncio
async def test_delete_task_preserves_other_tasks(todo_tools, session, test_user):
    """Test that deleting one task doesn't affect other tasks"""
    # Create multiple tasks
    task1 = Task(user_id=test_user.id, title="Task 1")
    task2 = Task(user_id=test_user.id, title="Task 2")
    task3 = Task(user_id=test_user.id, title="Task 3")

    session.add(task1)
    session.add(task2)
    session.add(task3)
    session.commit()
    session.refresh(task1)
    session.refresh(task2)
    session.refresh(task3)

    # Delete task2
    await todo_tools.delete_task(task_id=str(task2.id))

    # Verify task2 is deleted
    deleted_task = session.get(Task, task2.id)
    assert deleted_task is None

    # Verify task1 and task3 still exist
    remaining_task1 = session.get(Task, task1.id)
    remaining_task3 = session.get(Task, task3.id)

    assert remaining_task1 is not None
    assert remaining_task3 is not None
