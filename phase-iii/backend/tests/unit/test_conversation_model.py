"""
Unit tests for Conversation model
RED PHASE: These tests should FAIL until the model is implemented
"""
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Session, create_engine, SQLModel
from pydantic import ValidationError
from src.models.conversation import Conversation
from src.models.user import User  # Import to register table with SQLModel
from src.models.message import Message  # Import to register table with SQLModel


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


def test_conversation_model_creation(session):
    """Test creating a Conversation instance"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    assert conversation.user_id == user_id
    assert conversation.id is not None  # UUID generated on instantiation
    assert isinstance(conversation.id, UUID)
    assert conversation.created_at is not None
    assert conversation.updated_at is not None


def test_conversation_model_persistence(session):
    """Test persisting Conversation to database"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    assert conversation.id is not None
    assert isinstance(conversation.id, UUID)
    assert conversation.user_id == user_id


def test_conversation_timestamps(session):
    """Test that timestamps are auto-generated"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    assert isinstance(conversation.created_at, datetime)
    assert isinstance(conversation.updated_at, datetime)
    assert conversation.created_at <= conversation.updated_at


def test_conversation_user_id_required(session):
    """Test that user_id is required"""
    # SQLModel allows instantiation but should fail on database operations
    with pytest.raises(ValidationError):
        # This should fail validation
        conversation = Conversation.model_validate({})


def test_conversation_relationships(session):
    """Test that Conversation has messages relationship"""
    user_id = uuid4()
    conversation = Conversation(user_id=user_id)

    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    # Should have messages relationship (empty list initially)
    assert hasattr(conversation, 'messages')
    assert conversation.messages == []
