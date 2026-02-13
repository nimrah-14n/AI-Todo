"""
Integration tests for chat endpoint.
RED PHASE: These tests should FAIL until the endpoint is implemented
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from src.api.chat import app
from src.models.user import User
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


def test_chat_endpoint_exists(client):
    """Test that the chat endpoint exists"""
    user_id = str(uuid4())
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Hello"}
    )

    # Should not return 404
    assert response.status_code != 404


def test_chat_endpoint_creates_new_conversation(client, test_user, session):
    """Test that chat endpoint creates a new conversation if none exists"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello, create a task to buy groceries"}
    )

    assert response.status_code == 200

    # Check that a conversation was created
    conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).all()

    assert len(conversations) == 1


def test_chat_endpoint_uses_existing_conversation(client, test_user, session):
    """Test that chat endpoint uses existing conversation if conversation_id provided"""
    # Create a conversation
    conversation = Conversation(user_id=test_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "List my tasks",
            "conversation_id": str(conversation.id)
        }
    )

    assert response.status_code == 200

    # Should still have only one conversation
    conversations = session.query(Conversation).filter(
        Conversation.user_id == test_user.id
    ).all()

    assert len(conversations) == 1


def test_chat_endpoint_stores_user_message(client, test_user, session):
    """Test that user message is stored in database"""
    user_message = "Add a task to buy groceries"

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": user_message}
    )

    assert response.status_code == 200

    # Check that user message was stored
    messages = session.query(Message).filter(
        Message.user_id == test_user.id,
        Message.role == "user"
    ).all()

    assert len(messages) >= 1
    assert any(msg.content == user_message for msg in messages)


def test_chat_endpoint_stores_assistant_response(client, test_user, session):
    """Test that assistant response is stored in database"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 200

    # Check that assistant message was stored
    messages = session.query(Message).filter(
        Message.user_id == test_user.id,
        Message.role == "assistant"
    ).all()

    assert len(messages) >= 1


def test_chat_endpoint_returns_response(client, test_user):
    """Test that chat endpoint returns assistant response"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "response" in data
    assert isinstance(data["response"], str)
    assert len(data["response"]) > 0


def test_chat_endpoint_returns_conversation_id(client, test_user):
    """Test that chat endpoint returns conversation_id"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 200

    data = response.json()
    assert "conversation_id" in data
    assert isinstance(data["conversation_id"], str)


def test_chat_endpoint_loads_conversation_history(client, test_user, session):
    """Test that chat endpoint loads conversation history"""
    # Create a conversation with history
    conversation = Conversation(user_id=test_user.id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Add previous messages
    msg1 = Message(
        conversation_id=conversation.id,
        user_id=test_user.id,
        role="user",
        content="Add a task to buy groceries"
    )
    msg2 = Message(
        conversation_id=conversation.id,
        user_id=test_user.id,
        role="assistant",
        content="Task created successfully"
    )
    session.add(msg1)
    session.add(msg2)
    session.commit()

    # Send new message with conversation_id
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "What tasks do I have?",
            "conversation_id": str(conversation.id)
        }
    )

    assert response.status_code == 200

    # Agent should have access to history and respond appropriately


def test_chat_endpoint_validates_user_id(client):
    """Test that chat endpoint validates user_id format"""
    response = client.post(
        "/api/invalid-uuid/chat",
        json={"message": "Hello"}
    )

    # Should return validation error
    assert response.status_code in [400, 422]


def test_chat_endpoint_validates_message_required(client, test_user):
    """Test that chat endpoint requires message field"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={}
    )

    # Should return validation error
    assert response.status_code in [400, 422]


def test_chat_endpoint_stateless_cycle(client, test_user, session):
    """Test the complete stateless request-response cycle"""
    # 1. Send message (no conversation_id)
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Hello"}
    )

    assert response1.status_code == 200
    data1 = response1.json()
    conversation_id = data1["conversation_id"]

    # 2. Send another message with conversation_id
    response2 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Add a task",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200
    data2 = response2.json()

    # Should use same conversation
    assert data2["conversation_id"] == conversation_id

    # Verify messages are stored in order
    messages = session.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at).all()

    assert len(messages) >= 4  # 2 user + 2 assistant messages
