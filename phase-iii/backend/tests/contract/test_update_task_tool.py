"""
Contract tests for update_task MCP tool.
RED PHASE: These tests should FAIL until the tool is properly implemented

Contract tests verify that the tool adheres to its input/output schema
and handles partial updates correctly.
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
        description="Milk and eggs",
        is_complete=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.mark.asyncio
async def test_update_task_output_schema(todo_tools, sample_task):
    """Test that update_task returns correct output schema"""
    result = await todo_tools.update_task(
        task_id=str(sample_task.id),
        title="New title"
    )

    # Output must contain these fields
    assert "task_id" in result
    assert "title" in result
    assert "description" in result
    assert "message" in result

    # task_id must match input
    assert result["task_id"] == str(sample_task.id)

    # message must be a non-empty string
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0


@pytest.mark.asyncio
async def test_update_task_title_only(todo_tools, sample_task, session):
    """Test updating only the title"""
    new_title = "Buy groceries and snacks"
    original_description = sample_task.description

    result = await todo_tools.update_task(
        task_id=str(sample_task.id),
        title=new_title
    )

    # Refresh task from database
    session.refresh(sample_task)

    # Title should be updated
    assert sample_task.title == new_title

    # Description should remain unchanged
    assert sample_task.description == original_description


@pytest.mark.asyncio
async def test_update_task_description_only(todo_tools, sample_task, session):
    """Test updating only the description"""
    new_description = "Milk, eggs, bread, and cheese"
    original_title = sample_task.title

    result = await todo_tools.update_task(
        task_id=str(sample_task.id),
        description=new_description
    )

    # Refresh task from database
    session.refresh(sample_task)

    # Description should be updated
    assert sample_task.description == new_description

    # Title should remain unchanged
    assert sample_task.title == original_title


@pytest.mark.asyncio
async def test_update_task_both_fields(todo_tools, sample_task, session):
    """Test updating both title and description"""
    new_title = "Buy groceries for party"
    new_description = "Chips, dip, soda, and ice"

    result = await todo_tools.update_task(
        task_id=str(sample_task.id),
        title=new_title,
        description=new_description
    )

    # Refresh task from database
    session.refresh(sample_task)

    # Both should be updated
    assert sample_task.title == new_title
    assert sample_task.description == new_description


@pytest.mark.asyncio
async def test_update_task_invalid_uuid(todo_tools):
    """Test that update_task rejects invalid UUID format"""
    with pytest.raises(ValueError, match="Invalid task_id format"):
        await todo_tools.update_task(
            task_id="not-a-uuid",
            title="New title"
        )


@pytest.mark.asyncio
async def test_update_task_nonexistent_task(todo_tools):
    """Test that update_task rejects non-existent task"""
    fake_uuid = str(uuid4())

    with pytest.raises(ValueError, match="Task not found"):
        await todo_tools.update_task(
            task_id=fake_uuid,
            title="New title"
        )


@pytest.mark.asyncio
async def test_update_task_ownership_validation(session, sample_task):
    """Test that update_task validates task ownership"""
    # Create another user
    other_user = User(
        email="other@example.com",
        hashed_password="hashed_password_here"
    )
    session.add(other_user)
    session.commit()
    session.refresh(other_user)

    # Try to update task with wrong user
    other_tools = TodoTools(session=session, user_id=other_user.id)

    with pytest.raises(ValueError, match="does not belong to user"):
        await other_tools.update_task(
            task_id=str(sample_task.id),
            title="Hacked title"
        )


@pytest.mark.asyncio
async def test_update_task_title_validation_empty(todo_tools, sample_task):
    """Test that update_task rejects empty title"""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await todo_tools.update_task(
            task_id=str(sample_task.id),
            title=""
        )


@pytest.mark.asyncio
async def test_update_task_title_validation_whitespace(todo_tools, sample_task):
    """Test that update_task rejects whitespace-only title"""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await todo_tools.update_task(
            task_id=str(sample_task.id),
            title="   "
        )


@pytest.mark.asyncio
async def test_update_task_title_validation_too_long(todo_tools, sample_task):
    """Test that update_task rejects title longer than 200 characters"""
    long_title = "a" * 201

    with pytest.raises(ValueError, match="title must be 200 characters or less"):
        await todo_tools.update_task(
            task_id=str(sample_task.id),
            title=long_title
        )


@pytest.mark.asyncio
async def test_update_task_description_validation_too_long(todo_tools, sample_task):
    """Test that update_task rejects description longer than 1000 characters"""
    long_description = "a" * 1001

    with pytest.raises(ValueError, match="description must be 1000 characters or less"):
        await todo_tools.update_task(
            task_id=str(sample_task.id),
            description=long_description
        )


@pytest.mark.asyncio
async def test_update_task_strips_whitespace(todo_tools, sample_task, session):
    """Test that update_task strips leading/trailing whitespace"""
    result = await todo_tools.update_task(
        task_id=str(sample_task.id),
        title="  New title  "
    )

    session.refresh(sample_task)

    assert sample_task.title == "New title"


@pytest.mark.asyncio
async def test_update_task_updates_timestamp(todo_tools, sample_task, session):
    """Test that update_task updates the updated_at timestamp"""
    import time

    original_updated_at = sample_task.updated_at

    # Wait a bit to ensure timestamp difference
    time.sleep(0.01)

    await todo_tools.update_task(
        task_id=str(sample_task.id),
        title="New title"
    )

    session.refresh(sample_task)

    # Verify updated_at changed
    assert sample_task.updated_at > original_updated_at


@pytest.mark.asyncio
async def test_update_task_preserves_completion_status(todo_tools, session, test_user):
    """Test that update_task doesn't change completion status"""
    # Create a completed task
    task = Task(
        user_id=test_user.id,
        title="Completed task",
        is_complete=True
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Update the title
    await todo_tools.update_task(
        task_id=str(task.id),
        title="Updated completed task"
    )

    session.refresh(task)

    # Should still be complete
    assert task.is_complete is True


@pytest.mark.asyncio
async def test_update_task_clear_description(todo_tools, sample_task, session):
    """Test that update_task can clear description"""
    # Update with empty description
    await todo_tools.update_task(
        task_id=str(sample_task.id),
        description=""
    )

    session.refresh(sample_task)

    # Description should be None or empty
    assert sample_task.description is None or sample_task.description == ""


@pytest.mark.asyncio
async def test_update_task_confirmation_message(todo_tools, sample_task):
    """Test that update_task returns a helpful confirmation message"""
    result = await todo_tools.update_task(
        task_id=str(sample_task.id),
        title="New title"
    )

    message = result["message"].lower()

    # Message should mention update
    assert any(word in message for word in ["update", "updated", "changed"])

    # Message should mention the task
    assert "task" in message or "new title" in message.lower()
