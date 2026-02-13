"""
Integration tests for conversation persistence.
RED PHASE: These tests should FAIL until the feature is implemented

Tests verify that conversations are persisted and can be resumed after interruption.
"""
import pytest
from fastapi.testclient import TestClient
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


def test_list_user_conversations(client, test_user, session):
    """Test listing all conversations for a user"""
    # Create multiple conversations with messages
    conv1 = Conversation(user_id=test_user.id)
    conv2 = Conversation(user_id=test_user.id)
    session.add(conv1)
    session.add(conv2)
    session.commit()
    session.refresh(conv1)
    session.refresh(conv2)

    # Add messages to conversations
    msg1 = Message(conversation_id=conv1.id, user_id=test_user.id, role="user", content="Hello")
    msg2 = Message(conversation_id=conv2.id, user_id=test_user.id, role="user", content="Hi there")
    session.add(msg1)
    session.add(msg2)
    session.commit()

    # List conversations
    response = client.get(f"/api/{test_user.id}/conversations")

    assert response.status_code == 200

    data = response.json()
    assert "conversations" in data
    assert len(data["conversations"]) == 2


def test_list_conversations_ordered_by_updated_at(client, test_user, session):
    """Test that conversations are ordered by most recent first"""
    import time

    # Create conversations with time delays
    conv1 = Conversation(user_id=test_user.id)
    session.add(conv1)
    session.commit()
    session.refresh(conv1)

    time.sleep(0.01)

    conv2 = Conversation(user_id=test_user.id)
    session.add(conv2)
    session.commit()
    session.refresh(conv2)

    # List conversations
    response = client.get(f"/api/{test_user.id}/conversations")

    assert response.status_code == 200

    data = response.json()
    conversations = data["conversations"]

    # Most recent should be first
    assert conversations[0]["id"] == str(conv2.id)
    assert conversations[1]["id"] == str(conv1.id)


def test_get_conversation_history(client, test_user, session):
    """Test retrieving conversation history"""
    # Create conversation with messages
    conv = Conversation(user_id=test_user.id)
    session.add(conv)
    session.commit()
    session.refresh(conv)

    # Add messages
    messages = [
        Message(conversation_id=conv.id, user_id=test_user.id, role="user", content="Hello"),
        Message(conversation_id=conv.id, user_id=test_user.id, role="assistant", content="Hi! How can I help?"),
        Message(conversation_id=conv.id, user_id=test_user.id, role="user", content="Add a task"),
        Message(conversation_id=conv.id, user_id=test_user.id, role="assistant", content="Task created!"),
    ]
    for msg in messages:
        session.add(msg)
    session.commit()

    # Get conversation history
    response = client.get(f"/api/{test_user.id}/conversations/{conv.id}")

    assert response.status_code == 200

    data = response.json()
    assert "messages" in data
    assert len(data["messages"]) == 4


def test_get_conversation_history_ordered_chronologically(client, test_user, session):
    """Test that messages are returned in chronological order"""
    # Create conversation with messages
    conv = Conversation(user_id=test_user.id)
    session.add(conv)
    session.commit()
    session.refresh(conv)

    # Add messages
    msg1 = Message(conversation_id=conv.id, user_id=test_user.id, role="user", content="First")
    msg2 = Message(conversation_id=conv.id, user_id=test_user.id, role="assistant", content="Second")
    msg3 = Message(conversation_id=conv.id, user_id=test_user.id, role="user", content="Third")
    session.add(msg1)
    session.add(msg2)
    session.add(msg3)
    session.commit()

    # Get conversation history
    response = client.get(f"/api/{test_user.id}/conversations/{conv.id}")

    assert response.status_code == 200

    data = response.json()
    messages = data["messages"]

    # Should be in chronological order
    assert messages[0]["content"] == "First"
    assert messages[1]["content"] == "Second"
    assert messages[2]["content"] == "Third"


def test_get_conversation_history_limits_messages(client, test_user, session):
    """Test that conversation history is limited to last 50 messages"""
    # Create conversation with many messages
    conv = Conversation(user_id=test_user.id)
    session.add(conv)
    session.commit()
    session.refresh(conv)

    # Add 60 messages
    for i in range(60):
        msg = Message(
            conversation_id=conv.id,
            user_id=test_user.id,
            role="user" if i % 2 == 0 else "assistant",
            content=f"Message {i}"
        )
        session.add(msg)
    session.commit()

    # Get conversation history
    response = client.get(f"/api/{test_user.id}/conversations/{conv.id}")

    assert response.status_code == 200

    data = response.json()
    messages = data["messages"]

    # Should be limited to 50 messages
    assert len(messages) <= 50

    # Should be the most recent 50
    if len(messages) == 50:
        assert "Message 10" in messages[0]["content"] or int(messages[0]["content"].split()[-1]) >= 10


def test_get_nonexistent_conversation(client, test_user):
    """Test getting a conversation that doesn't exist"""
    from uuid import uuid4
    fake_id = str(uuid4())

    response = client.get(f"/api/{test_user.id}/conversations/{fake_id}")

    assert response.status_code == 404


def test_get_conversation_ownership_validation(client, session):
    """Test that users can only access their own conversations"""
    # Create two users
    user1 = User(email="user1@example.com", hashed_password="hash1")
    user2 = User(email="user2@example.com", hashed_password="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # User 1's conversation
    conv1 = Conversation(user_id=user1.id)
    session.add(conv1)
    session.commit()
    session.refresh(conv1)

    # User 2 tries to access User 1's conversation
    response = client.get(f"/api/{user2.id}/conversations/{conv1.id}")

    assert response.status_code == 403


def test_list_conversations_only_shows_user_conversations(client, session):
    """Test that users only see their own conversations"""
    # Create two users
    user1 = User(email="user1@example.com", hashed_password="hash1")
    user2 = User(email="user2@example.com", hashed_password="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # Create conversations for each user
    conv1 = Conversation(user_id=user1.id)
    conv2 = Conversation(user_id=user2.id)
    session.add(conv1)
    session.add(conv2)
    session.commit()

    # User 1 lists conversations
    response = client.get(f"/api/{user1.id}/conversations")

    assert response.status_code == 200

    data = response.json()
    conversations = data["conversations"]

    # Should only see their own conversation
    assert len(conversations) == 1
    assert conversations[0]["id"] == str(conv1.id)


def test_resume_conversation_after_interruption(client, test_user, session):
    """Test the full flow of resuming a conversation"""
    # Step 1: Start a conversation
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to buy groceries"}
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Step 2: Simulate interruption (close browser, etc.)
    # ...

    # Step 3: List conversations to find the previous one
    response2 = client.get(f"/api/{test_user.id}/conversations")

    assert response2.status_code == 200
    conversations = response2.json()["conversations"]
    assert len(conversations) >= 1

    # Step 4: Get conversation history
    response3 = client.get(f"/api/{test_user.id}/conversations/{conversation_id}")

    assert response3.status_code == 200
    history = response3.json()["messages"]
    assert len(history) >= 2

    # Step 5: Continue the conversation
    response4 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Show me my tasks",
            "conversation_id": conversation_id
        }
    )

    assert response4.status_code == 200

    # Verify conversation continues with same ID
    assert response4.json()["conversation_id"] == conversation_id


def test_conversation_list_includes_metadata(client, test_user, session):
    """Test that conversation list includes useful metadata"""
    # Create conversation with messages
    conv = Conversation(user_id=test_user.id)
    session.add(conv)
    session.commit()
    session.refresh(conv)

    msg = Message(conversation_id=conv.id, user_id=test_user.id, role="user", content="Hello")
    session.add(msg)
    session.commit()

    # List conversations
    response = client.get(f"/api/{test_user.id}/conversations")

    assert response.status_code == 200

    data = response.json()
    conversations = data["conversations"]

    # Each conversation should have metadata
    assert "id" in conversations[0]
    assert "created_at" in conversations[0]
    assert "updated_at" in conversations[0]


def test_empty_conversation_list(client, test_user):
    """Test listing conversations when user has none"""
    response = client.get(f"/api/{test_user.id}/conversations")

    assert response.status_code == 200

    data = response.json()
    assert "conversations" in data
    assert data["conversations"] == []
