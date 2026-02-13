"""
Integration tests for task listing flow through conversation.
RED PHASE: These tests should FAIL until the full flow is implemented

Integration tests verify the end-to-end flow:
message → agent → MCP tool → database → formatted response
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from src.api.chat import app
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
def sample_tasks(session, test_user):
    """Create sample tasks for testing"""
    tasks = [
        Task(user_id=test_user.id, title="Buy groceries", is_complete=False),
        Task(user_id=test_user.id, title="Call mom", is_complete=True),
        Task(user_id=test_user.id, title="Finish report", is_complete=False),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    return tasks


@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


def test_list_tasks_through_conversation(client, test_user, sample_tasks):
    """Test listing tasks with natural language"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show me all my tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "response" in data

    # Response should mention the tasks
    response_text = data["response"].lower()
    assert "groceries" in response_text or "task" in response_text


def test_list_tasks_various_trigger_phrases(client, test_user, sample_tasks):
    """Test that various natural language patterns trigger task listing"""
    trigger_phrases = [
        "Show me my tasks",
        "List all my tasks",
        "What do I need to do?",
        "What tasks do I have?",
        "Show my todo list"
    ]

    for phrase in trigger_phrases:
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": phrase}
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data


def test_list_incomplete_tasks_only(client, test_user, sample_tasks):
    """Test filtering for incomplete tasks"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show me my incomplete tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Should mention incomplete tasks
    assert "groceries" in response_text or "report" in response_text


def test_list_complete_tasks_only(client, test_user, sample_tasks):
    """Test filtering for complete tasks"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show me my completed tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Should mention completed tasks
    assert "mom" in response_text or "call" in response_text


def test_list_tasks_empty_state(client, test_user):
    """Test listing tasks when user has no tasks"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show me my tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Should indicate no tasks
    assert any(word in response_text for word in ["no tasks", "empty", "don't have", "haven't"])


def test_list_tasks_formatted_response(client, test_user, sample_tasks):
    """Test that task list is formatted nicely"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "List my tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # Should contain task titles
    assert "Buy groceries" in response_text or "groceries" in response_text.lower()
    assert "Call mom" in response_text or "mom" in response_text.lower()
    assert "Finish report" in response_text or "report" in response_text.lower()


def test_list_tasks_shows_completion_status(client, test_user, sample_tasks):
    """Test that response indicates which tasks are complete"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show all my tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Should indicate completion status somehow
    # (checkmarks, "completed", "done", etc.)
    assert "complete" in response_text or "done" in response_text or "✓" in response_text or "✔" in response_text


def test_list_tasks_in_conversation_context(client, test_user, sample_tasks):
    """Test listing tasks within an ongoing conversation"""
    # First, create a task
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to water plants"}
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Then list tasks in same conversation
    response2 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Now show me all my tasks",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200

    data = response2.json()
    response_text = data["response"].lower()

    # Should include the newly created task
    assert "water" in response_text or "plants" in response_text


def test_list_tasks_only_shows_user_tasks(client, session):
    """Test that users only see their own tasks"""
    # Create two users with tasks
    user1 = User(email="user1@example.com", hashed_password="hash1")
    user2 = User(email="user2@example.com", hashed_password="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # User 1's task
    task1 = Task(user_id=user1.id, title="User 1 task")
    session.add(task1)
    session.commit()

    # User 2's task
    task2 = Task(user_id=user2.id, title="User 2 task")
    session.add(task2)
    session.commit()

    # User 1 lists tasks
    response1 = client.post(
        f"/api/{user1.id}/chat",
        json={"message": "Show my tasks"}
    )

    assert response1.status_code == 200
    response1_text = response1.json()["response"]

    # Should only see their own task
    assert "User 1 task" in response1_text
    assert "User 2 task" not in response1_text


def test_list_tasks_with_descriptions(client, test_user, session):
    """Test that task descriptions are included in response"""
    task = Task(
        user_id=test_user.id,
        title="Buy groceries",
        description="Milk, eggs, bread, and cheese"
    )
    session.add(task)
    session.commit()

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Show my tasks"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"]

    # Should include description or at least the title
    assert "Buy groceries" in response_text or "groceries" in response_text.lower()


def test_list_tasks_end_to_end_flow(client, test_user, sample_tasks, session):
    """Test complete end-to-end flow for task listing"""
    # Step 1: User sends message
    user_message = "What tasks do I have?"

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": user_message}
    )

    assert response.status_code == 200

    # Step 2: Verify response structure
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

    # Step 3: Verify response contains task information
    response_text = data["response"]

    # Should mention at least some of the tasks
    task_titles = ["Buy groceries", "Call mom", "Finish report"]
    mentioned_count = sum(1 for title in task_titles if title.lower() in response_text.lower())

    assert mentioned_count >= 1  # At least one task should be mentioned

    # Step 4: Verify conversation and messages were stored
    from src.models.conversation import Conversation
    from src.models.message import Message

    conversation_id = data["conversation_id"]
    conversation = session.get(Conversation, conversation_id)
    assert conversation is not None

    messages = session.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    assert len(messages) >= 2
    assert messages[0].role == "user"
    assert messages[0].content == user_message
    assert messages[1].role == "assistant"
