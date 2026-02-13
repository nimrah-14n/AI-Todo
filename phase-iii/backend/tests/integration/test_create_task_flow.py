"""
Integration tests for task creation flow through conversation.
RED PHASE: These tests should FAIL until the full flow is implemented

Integration tests verify the end-to-end flow:
message → agent → MCP tool → database → response
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from src.api.chat import app
from src.models.user import User
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message


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
def client():
    """Create FastAPI test client"""
    return TestClient(app)


def test_create_task_through_conversation_simple(client, test_user, session):
    """Test creating a task with simple natural language"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response.status_code == 200

    # Verify task was created in database
    tasks = session.query(Task).filter(Task.user_id == test_user.id).all()

    assert len(tasks) == 1
    assert "groceries" in tasks[0].title.lower() or "buy groceries" in tasks[0].title.lower()
    assert tasks[0].is_complete is False


def test_create_task_with_description(client, test_user, session):
    """Test creating a task with description through conversation"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Create a task to buy groceries with milk, eggs, and bread"}
    )

    assert response.status_code == 200

    # Verify task was created
    tasks = session.query(Task).filter(Task.user_id == test_user.id).all()

    assert len(tasks) == 1
    # Description might contain the details
    task = tasks[0]
    assert task.description is not None or "milk" in task.title.lower()


def test_create_multiple_tasks_in_conversation(client, test_user, session):
    """Test creating multiple tasks in the same conversation"""
    # First task
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Second task in same conversation
    response2 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Also add a task to call mom",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200

    # Verify both tasks were created
    tasks = session.query(Task).filter(Task.user_id == test_user.id).all()

    assert len(tasks) == 2


def test_create_task_response_includes_confirmation(client, test_user):
    """Test that agent responds with confirmation after creating task"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "response" in data

    # Response should mention task creation
    response_text = data["response"].lower()
    assert any(word in response_text for word in ["created", "added", "task", "groceries"])


def test_create_task_stores_conversation_messages(client, test_user, session):
    """Test that user message and agent response are stored"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response.status_code == 200

    conversation_id = response.json()["conversation_id"]

    # Verify messages were stored
    messages = session.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    assert len(messages) >= 2  # At least user message and assistant response

    # First message should be from user
    assert messages[0].role == "user"
    assert "buy groceries" in messages[0].content.lower()

    # Second message should be from assistant
    assert messages[1].role == "assistant"


def test_create_task_with_various_trigger_words(client, test_user, session):
    """Test that various natural language patterns trigger task creation"""
    trigger_phrases = [
        "Add a task to buy milk",
        "Create a reminder to call John",
        "Remember to finish the report",
        "I need to buy groceries",
        "Todo: clean the house"
    ]

    for phrase in trigger_phrases:
        # Create new conversation for each test
        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": phrase}
        )

        assert response.status_code == 200

    # Verify all tasks were created
    tasks = session.query(Task).filter(Task.user_id == test_user.id).all()

    assert len(tasks) == len(trigger_phrases)


def test_create_task_validates_title_length(client, test_user, session):
    """Test that task creation respects title length limits"""
    # Title that's too long (over 200 characters)
    long_title = "a" * 250

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": f"Add a task: {long_title}"}
    )

    assert response.status_code == 200

    # Agent should handle this gracefully
    # Either truncate or inform user
    data = response.json()
    assert "response" in data


def test_create_task_belongs_to_correct_user(client, session):
    """Test that tasks are associated with the correct user"""
    # Create two users
    user1 = User(email="user1@example.com", hashed_password="hash1")
    user2 = User(email="user2@example.com", hashed_password="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # User 1 creates a task
    response1 = client.post(
        f"/api/{user1.id}/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response1.status_code == 200

    # User 2 creates a task
    response2 = client.post(
        f"/api/{user2.id}/chat",
        json={"message": "Add a task to call mom"}
    )

    assert response2.status_code == 200

    # Verify each user has only their own task
    user1_tasks = session.query(Task).filter(Task.user_id == user1.id).all()
    user2_tasks = session.query(Task).filter(Task.user_id == user2.id).all()

    assert len(user1_tasks) == 1
    assert len(user2_tasks) == 1
    assert "groceries" in user1_tasks[0].title.lower()
    assert "mom" in user2_tasks[0].title.lower()


def test_create_task_end_to_end_flow(client, test_user, session):
    """Test complete end-to-end flow for task creation"""
    # Step 1: User sends message
    user_message = "Add a task to buy groceries for the party"

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": user_message}
    )

    assert response.status_code == 200

    # Step 2: Verify response structure
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

    conversation_id = data["conversation_id"]

    # Step 3: Verify task in database
    tasks = session.query(Task).filter(Task.user_id == test_user.id).all()

    assert len(tasks) == 1
    task = tasks[0]
    assert task.user_id == test_user.id
    assert task.is_complete is False
    assert task.title is not None
    assert len(task.title) > 0

    # Step 4: Verify conversation and messages
    conversation = session.get(Conversation, conversation_id)
    assert conversation is not None
    assert conversation.user_id == test_user.id

    messages = session.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    assert len(messages) >= 2
    assert messages[0].role == "user"
    assert messages[0].content == user_message
    assert messages[1].role == "assistant"

    # Step 5: Verify agent response mentions the task
    assert "task" in data["response"].lower() or "groceries" in data["response"].lower()
