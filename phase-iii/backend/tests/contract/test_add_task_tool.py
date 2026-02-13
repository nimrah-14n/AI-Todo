"""
Contract tests for add_task MCP tool.
RED PHASE: These tests should FAIL until the tool is properly implemented

Contract tests verify that the tool adheres to its input/output schema
and handles validation errors correctly.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from src.mcp.tools import TodoTools
from src.models.user import User


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


@pytest.mark.asyncio
async def test_add_task_input_schema_valid(todo_tools):
    """Test that add_task accepts valid input according to schema"""
    # Valid input: title only
    result = await todo_tools.add_task(title="Buy groceries")

    assert result is not None
    assert "task_id" in result
    assert "title" in result
    assert "message" in result
    assert result["title"] == "Buy groceries"


@pytest.mark.asyncio
async def test_add_task_input_schema_with_description(todo_tools):
    """Test that add_task accepts title and description"""
    result = await todo_tools.add_task(
        title="Buy groceries",
        description="Milk, eggs, bread"
    )

    assert result is not None
    assert "task_id" in result
    assert result["title"] == "Buy groceries"


@pytest.mark.asyncio
async def test_add_task_output_schema(todo_tools):
    """Test that add_task returns correct output schema"""
    result = await todo_tools.add_task(title="Test task")

    # Output must contain these fields
    assert "task_id" in result
    assert "title" in result
    assert "message" in result

    # task_id must be a valid UUID string
    assert isinstance(result["task_id"], str)
    try:
        uuid4_obj = uuid4()
        # Verify it's a valid UUID format
        from uuid import UUID
        UUID(result["task_id"])
    except ValueError:
        pytest.fail("task_id is not a valid UUID")

    # title must match input
    assert result["title"] == "Test task"

    # message must be a non-empty string
    assert isinstance(result["message"], str)
    assert len(result["message"]) > 0


@pytest.mark.asyncio
async def test_add_task_validation_empty_title(todo_tools):
    """Test that add_task rejects empty title"""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await todo_tools.add_task(title="")


@pytest.mark.asyncio
async def test_add_task_validation_whitespace_title(todo_tools):
    """Test that add_task rejects whitespace-only title"""
    with pytest.raises(ValueError, match="title cannot be empty"):
        await todo_tools.add_task(title="   ")


@pytest.mark.asyncio
async def test_add_task_validation_title_too_long(todo_tools):
    """Test that add_task rejects title longer than 200 characters"""
    long_title = "a" * 201

    with pytest.raises(ValueError, match="title must be 200 characters or less"):
        await todo_tools.add_task(title=long_title)


@pytest.mark.asyncio
async def test_add_task_validation_title_max_length(todo_tools):
    """Test that add_task accepts title at max length (200 characters)"""
    max_title = "a" * 200

    result = await todo_tools.add_task(title=max_title)

    assert result is not None
    assert result["title"] == max_title


@pytest.mark.asyncio
async def test_add_task_validation_description_too_long(todo_tools):
    """Test that add_task rejects description longer than 1000 characters"""
    long_description = "a" * 1001

    with pytest.raises(ValueError, match="description must be 1000 characters or less"):
        await todo_tools.add_task(
            title="Valid title",
            description=long_description
        )


@pytest.mark.asyncio
async def test_add_task_validation_description_max_length(todo_tools):
    """Test that add_task accepts description at max length (1000 characters)"""
    max_description = "a" * 1000

    result = await todo_tools.add_task(
        title="Valid title",
        description=max_description
    )

    assert result is not None


@pytest.mark.asyncio
async def test_add_task_strips_whitespace(todo_tools):
    """Test that add_task strips leading/trailing whitespace from title"""
    result = await todo_tools.add_task(title="  Buy groceries  ")

    assert result["title"] == "Buy groceries"


@pytest.mark.asyncio
async def test_add_task_optional_description(todo_tools):
    """Test that description is optional"""
    result = await todo_tools.add_task(title="Task without description")

    assert result is not None
    assert "task_id" in result


@pytest.mark.asyncio
async def test_add_task_creates_incomplete_task(todo_tools, session):
    """Test that newly created tasks are marked as incomplete"""
    from src.models.task import Task

    result = await todo_tools.add_task(title="New task")

    # Fetch the task from database
    task = session.get(Task, result["task_id"])

    assert task is not None
    assert task.is_complete is False
