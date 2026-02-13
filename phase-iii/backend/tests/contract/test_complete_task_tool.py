"""
Contract tests for complete_task MCP tool.
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
    """Create a sample incomplete task"""
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
async def test_complete_task_output_schema(todo_tools, sample_task):
    """Test that complete_task returns correct output schema"""
    result = await todo_tools.complete_task(task_id=str(sample_task.id))

    # Output must contain these fields
    assert "task_id" in result
    assert "title" in result
    assert "message" in result

    # task_id must match input
    assert result["task_id"] == str(sample_task.id)

    # title must be present
    assert result["title"] == sample_task.title

    # message must be a non-empty string
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0


@pytest.mark.asyncio
async def test_complete_task_updates_status(todo_tools, sample_task, session):
    """Test that complete_task actually updates the task status"""
    # Verify task is initially incomplete
    assert sample_task.is_complete is False

    # Complete the task
    result = await todo_tools.complete_task(task_id=str(sample_task.id))

    # Refresh task from database
    session.refresh(sample_task)

    # Verify task is now complete
    assert sample_task.is_complete is True


@pytest.mark.asyncio
async def test_complete_task_invalid_uuid(todo_tools):
    """Test that complete_task rejects invalid UUID format"""
    with pytest.raises(ValueError, match="Invalid task_id format"):
        await todo_tools.complete_task(task_id="not-a-uuid")


@pytest.mark.asyncio
async def test_complete_task_nonexistent_task(todo_tools):
    """Test that complete_task rejects non-existent task"""
    fake_uuid = str(uuid4())

    with pytest.raises(ValueError, match="Task not found"):
        await todo_tools.complete_task(task_id=fake_uuid)


@pytest.mark.asyncio
async def test_complete_task_ownership_validation(session, sample_task):
    """Test that complete_task validates task ownership"""
    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_password_here"
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Try to complete task with wrong user
    other_tools = TodoTools(session=session, user_id=other_user.id)

    with pytest.raises(ValueError, match="does not belong to user"):
        await other_tools.complete_task(task_id=str(sample_task.id))


@pytest.mark.asyncio
async def test_complete_task_already_complete(todo_tools, session, test_user):
    """Test completing a task that's already complete"""
    # Create a complete task
    task = Task(
        user_id=test_user.id,
        title="Already done",
        is_complete=True
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Should still succeed (idempotent)
    result = await todo_tools.complete_task(task_id=str(task.id))

    assert result is not None
    assert result["task_id"] == str(task.id)


@pytest.mark.asyncio
async def test_complete_task_updates_timestamp(todo_tools, sample_task, session):
    """Test that complete_task updates the updated_at timestamp"""
    import time

    original_updated_at = sample_task.updated_at

    # Wait a bit to ensure timestamp difference
    time.sleep(0.01)

    # Complete the task
    await todo_tools.complete_task(task_id=str(sample_task.id))

    # Refresh task from database
    session.refresh(sample_task)

    # Verify updated_at changed
    assert sample_task.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_complete_task_preserves_other_fields(todo_tools, session, test_user):
    """Test that complete_task doesn't modify other task fields"""
    # Create task with description
    task = Task(
        user_id=test_user.id,
        title="Task with description",
        description="Important details",
        is_complete=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    original_title = task.title
    original_description = task.description
    original_created_at = task.created_at

    # Complete the task
    await todo_tools.complete_task(task_id=str(task.id))

    # Refresh task from database
    session.refresh(task)

    # Verify other fields unchanged
    assert task.title == original_title
    assert task.description == original_description
    assert task.created_at == original_created_at
    assert task.user_id == test_user.id


@pytest.mark.asyncio
async def test_complete_task_confirmation_message(todo_tools, sample_task):
    """Test that complete_task returns a helpful confirmation message"""
    result = await todo_tools.complete_task(task_id=str(sample_task.id))

    message = result["message"].lower()

    # Message should mention completion
    assert any(word in message for word in ["complete", "done", "marked", "finished"])

    # Message should mention the task title
    assert sample_task.title.lower() in message or "task" in message
