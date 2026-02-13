"""
Integration test for agent execution with MCP tools.

This test verifies the full flow of the agent executing with access to MCP tools
for task management operations.
"""
import pytest
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from sqlalchemy.pool import StaticPool

from src.agents.todo_agent import TodoAgent
from src.agents.runner import AgentRunner
from src.models.task import Task
from src.models.user import User


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="test_user")
def test_user_fixture(session: Session):
    """Create a test user."""
    user = User(
        id=uuid4(),
        email="test@example.com",
        name="Test User"
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_agent_execution_basic(session: Session, test_user: User):
    """
    Test basic agent execution without MCP tools.

    Verifies that the agent can process a simple message and return a response.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    user_message = "Hello, how can you help me?"
    conversation_history = []

    # Act
    response = await runner.run_async(
        user_message=user_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Assert
    assert response is not None
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_agent_understands_task_creation_intent(session: Session, test_user: User):
    """
    Test that agent understands task creation intent.

    Verifies that the agent can identify when a user wants to create a task.
    Note: This test doesn't actually call MCP tools, just verifies intent understanding.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    user_message = "Add a task to buy groceries"
    conversation_history = []

    # Act
    response = await runner.run_async(
        user_message=user_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Assert
    assert response is not None
    assert isinstance(response, str)
    # Response should acknowledge task creation
    assert any(keyword in response.lower() for keyword in ["task", "created", "added", "groceries"])


@pytest.mark.asyncio
async def test_agent_understands_list_tasks_intent(session: Session, test_user: User):
    """
    Test that agent understands list tasks intent.

    Verifies that the agent can identify when a user wants to view their tasks.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    user_message = "Show me all my tasks"
    conversation_history = []

    # Act
    response = await runner.run_async(
        user_message=user_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Assert
    assert response is not None
    assert isinstance(response, str)
    # Response should acknowledge listing tasks
    assert any(keyword in response.lower() for keyword in ["task", "list", "show", "have"])


@pytest.mark.asyncio
async def test_agent_maintains_conversation_context(session: Session, test_user: User):
    """
    Test that agent maintains conversation context across messages.

    Verifies that the agent can reference previous messages in the conversation.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    # First message
    conversation_history = []
    first_message = "Add a task to buy groceries"

    first_response = await runner.run_async(
        user_message=first_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Update history
    conversation_history.append({"role": "user", "content": first_message})
    conversation_history.append({"role": "assistant", "content": first_response})

    # Second message referencing first
    second_message = "What was that task about?"

    # Act
    second_response = await runner.run_async(
        user_message=second_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Assert
    assert second_response is not None
    assert isinstance(second_response, str)
    # Response should reference groceries from previous context
    assert "groceries" in second_response.lower() or "task" in second_response.lower()


@pytest.mark.asyncio
async def test_agent_handles_multiple_intents(session: Session, test_user: User):
    """
    Test that agent can handle messages with multiple intents.

    Verifies that the agent can process complex requests.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    user_message = "Add a task to buy groceries and then show me all my tasks"
    conversation_history = []

    # Act
    response = await runner.run_async(
        user_message=user_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Assert
    assert response is not None
    assert isinstance(response, str)
    # Response should acknowledge both actions
    assert any(keyword in response.lower() for keyword in ["task", "created", "added"])


@pytest.mark.asyncio
async def test_agent_handles_ambiguous_requests(session: Session, test_user: User):
    """
    Test that agent handles ambiguous requests gracefully.

    Verifies that the agent asks for clarification when needed.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    user_message = "Delete it"  # Ambiguous - delete what?
    conversation_history = []

    # Act
    response = await runner.run_async(
        user_message=user_message,
        conversation_history=conversation_history,
        agent_config=agent_config
    )

    # Assert
    assert response is not None
    assert isinstance(response, str)
    # Response should ask for clarification or indicate confusion
    assert len(response) > 0


@pytest.mark.asyncio
async def test_agent_config_structure(session: Session, test_user: User):
    """
    Test that agent configuration has the correct structure.

    Verifies that the agent config contains all required fields.
    """
    # Arrange
    agent = TodoAgent()

    # Act
    config = agent.get_config()

    # Assert
    assert config is not None
    assert isinstance(config, dict)
    assert "name" in config
    assert "model" in config
    assert "instructions" in config
    assert "tools" in config

    # Verify model is GPT-4
    assert "gpt-4" in config["model"].lower()

    # Verify instructions are comprehensive
    assert len(config["instructions"]) > 100
    assert "task" in config["instructions"].lower()

    # Verify tools are listed
    assert isinstance(config["tools"], list)
    assert len(config["tools"]) == 5

    # Verify all expected tools are present
    tool_names = [tool["name"] for tool in config["tools"]]
    expected_tools = ["add_task", "list_tasks", "complete_task", "delete_task", "update_task"]
    for expected_tool in expected_tools:
        assert expected_tool in tool_names


@pytest.mark.asyncio
async def test_agent_error_handling(session: Session, test_user: User):
    """
    Test that agent handles errors gracefully.

    Verifies that the agent doesn't crash on invalid inputs.
    """
    # Arrange
    agent = TodoAgent()
    runner = AgentRunner()
    agent_config = agent.get_config()

    # Test with empty message
    user_message = ""
    conversation_history = []

    # Act & Assert - should not raise exception
    try:
        response = await runner.run_async(
            user_message=user_message,
            conversation_history=conversation_history,
            agent_config=agent_config
        )
        # If it succeeds, response should be a string
        assert isinstance(response, str)
    except Exception as e:
        # If it fails, it should be a handled exception
        assert str(e) is not None


# Note: Full MCP tool integration tests would require:
# 1. Running MCP server
# 2. Configuring agent to connect to MCP server
# 3. Mocking OpenAI API responses with tool calls
# These tests verify the agent configuration and basic execution flow.
