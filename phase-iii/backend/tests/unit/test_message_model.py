"""
Unit tests for Message model
RED PHASE: These tests should FAIL until the model is implemented
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Session, create_engine, SQLModel
from pydantic import ValidationError
from src.models.message import Message, MessageRole
from src.models.conversation import Conversation
from src.models.user import User  # Import to register table with SQLModel


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
def conversation(session):
    """Create a test conversation"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


def test_message_model_creation(conversation):
    """Test creating a Message instance"""
    message = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.USER,
        content="Hello, world!"
    )

    assert message.conversation_id == conversation.id
    assert message.user_id == conversation.user_id
    assert message.role == MessageRole.USER
    assert message.content == "Hello, world!"
    assert message.id is not None  # UUID generated on instantiation
    assert isinstance(message.id, UUID)
    assert message.created_at is not None


def test_message_model_persistence(session, conversation):
    """Test persisting Message to database"""
    message = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.ASSISTANT,
        content="Hello! How can I help you?"
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    assert message.id is not None
    assert isinstance(message.id, UUID)
    assert message.conversation_id == conversation.id
    assert message.user_id == conversation.user_id
    assert message.role == MessageRole.ASSISTANT
    assert message.content == "Hello! How can I help you?"


def test_message_timestamps(session, conversation):
    """Test that timestamps are auto-generated"""
    message = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.USER,
        content="Test message"
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    assert isinstance(message.created_at, datetime)


def test_message_role_enum():
    """Test that MessageRole enum has correct values"""
    assert MessageRole.USER == "user"
    assert MessageRole.ASSISTANT == "assistant"
    assert MessageRole.SYSTEM == "system"


def test_message_required_fields():
    """Test that required fields are enforced"""
    # Missing conversation_id
    with pytest.raises(ValidationError):
        Message.model_validate({"user_id": str(uuid4()), "role": "user", "content": "Test"})

    # Missing user_id
    with pytest.raises(ValidationError):
        Message.model_validate({"conversation_id": str(uuid4()), "role": "user", "content": "Test"})

    # Missing role
    with pytest.raises(ValidationError):
        Message.model_validate({"conversation_id": str(uuid4()), "user_id": str(uuid4()), "content": "Test"})

    # Missing content
    with pytest.raises(ValidationError):
        Message.model_validate({"conversation_id": str(uuid4()), "user_id": str(uuid4()), "role": "user"})


def test_message_conversation_relationship(session, conversation):
    """Test that Message has relationship to Conversation"""
    message = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.USER,
        content="Test message"
    )

    session.add(message)
    session.commit()
    session.refresh(message)

    # Should be able to access conversation through relationship
    assert hasattr(message, 'conversation')
    assert message.conversation.id == conversation.id


def test_conversation_messages_relationship(session, conversation):
    """Test that Conversation can access its messages"""
    # Create multiple messages
    message1 = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.USER,
        content="First message"
    )
    message2 = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.ASSISTANT,
        content="Second message"
    )

    session.add(message1)
    session.add(message2)
    session.commit()
    session.refresh(conversation)

    # Conversation should have messages list
    assert len(conversation.messages) == 2
    assert message1 in conversation.messages
    assert message2 in conversation.messages


def test_message_ordering(session, conversation):
    """Test that messages are ordered by created_at"""
    # Create messages in specific order
    message1 = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.USER,
        content="First"
    )
    session.add(message1)
    session.commit()

    message2 = Message(
        conversation_id=conversation.id,
        user_id=conversation.user_id,
        role=MessageRole.ASSISTANT,
        content="Second"
    )
    session.add(message2)
    session.commit()

    session.refresh(conversation)

    # Messages should be ordered by created_at
    assert conversation.messages[0].created_at <= conversation.messages[1].created_at
    assert conversation.messages[0].content == "First"
    assert conversation.messages[1].content == "Second"
