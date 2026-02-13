"""
Integration tests for task completion flow through conversation.
RED PHASE: These tests should FAIL until the full flow is implemented

Integration tests verify the end-to-end flow:
message → agent → task reference resolution → MCP tool → database update
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
        Task(user_id=test_user.id, title="Call mom", is_complete=False),
        Task(user_id=test_user.id, title="Finish report", is_complete=False),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


def test_complete_task_by_title_reference(client, test_user, sample_tasks, session):
    """Test completing a task by referencing its title"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Mark 'Buy groceries' as complete"}
    )

    assert response.status_code == 200

    # Verify task was marked complete in database
    task = session.get(Task, sample_tasks[0].id)
    assert task.is_complete is True


def test_complete_task_various_trigger_phrases(client, test_user, sample_tasks, session):
    """Test that various natural language patterns trigger task completion"""
    trigger_phrases = [
        "Mark 'Call mom' as done",
        "I finished the report",
        "Complete the groceries task",
        "I'm done with calling mom"
    ]

    for i, phrase in enumerate(trigger_phrases):
        # Create a new task for each test
        task = Task(user_id=test_user.id, title=f"Test task {i}", is_complete=False)
        session.add(task)
        session.commit()

        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": phrase}
        )

        assert response.status_code == 200


def test_complete_task_confirmation_response(client, test_user, sample_tasks):
    """Test that agent responds with confirmation after completing task"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Mark 'Buy groceries' as complete"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Response should mention completion
    assert any(word in response_text for word in ["complete", "done", "marked", "finished"])

    # Response should mention the task
    assert "groceries" in response_text or "task" in response_text


def test_complete_task_in_conversation_context(client, test_user, session):
    """Test completing a task within an ongoing conversation"""
    # First, create a task through conversation
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to water plants"}
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Then complete it in same conversation
    response2 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "I just finished watering the plants",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200

    # Verify task was completed
    tasks = session.query(Task).filter(
        Task.user_id == test_user.id,
        Task.title.contains("water")
    ).all()

    assert len(tasks) >= 1
    # At least one should be complete
    assert any(task.is_complete for task in tasks)


def test_complete_nonexistent_task(client, test_user):
    """Test handling of completing a task that doesn't exist"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Mark 'Nonexistent task' as complete"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Agent should indicate task not found
    assert any(word in response_text for word in ["not found", "don't have", "couldn't find", "no task"])


def test_complete_task_only_affects_user_tasks(client, session):
    """Test that users can only complete their own tasks"""
    # Create two users with tasks
    user1 = User(email="user1@example.com", hashed_password="hash1")
    user2 = User(email="user2@example.com", hashed_password="hash2")
    session.add(user1)
    session.add(user2)
    session.commit()
    session.refresh(user1)
    session.refresh(user2)

    # User 1's task
    task1 = Task(user_id=user1.id, title="User 1 task", is_complete=False)
    session.add(task1)
    session.commit()

    # User 2 tries to complete User 1's task (should fail)
    response = client.post(
        f"/api/{user2.id}/chat",
        json={"message": "Mark 'User 1 task' as complete"}
    )

    assert response.status_code == 200

    # Task should still be incomplete
    session.refresh(task1)
    assert task1.is_complete is False


def test_complete_task_case_insensitive_matching(client, test_user, session):
    """Test that task title matching is case-insensitive"""
    task = Task(user_id=test_user.id, title="Buy Groceries", is_complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Use lowercase in message
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Mark 'buy groceries' as done"}
    )

    assert response.status_code == 200

    # Task should be complete
    session.refresh(task)
    assert task.is_complete is True


def test_complete_task_partial_title_match(client, test_user, session):
    """Test that partial title matching works"""
    task = Task(user_id=test_user.id, title="Buy groceries for the party", is_complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Use partial title
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Mark 'groceries' as complete"}
    )

    assert response.status_code == 200

    # Task should be complete
    session.refresh(task)
    assert task.is_complete is True


def test_complete_already_complete_task(client, test_user, session):
    """Test completing a task that's already complete (idempotent)"""
    task = Task(user_id=test_user.id, title="Already done", is_complete=True)
    session.add(task)
    session.commit()

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Mark 'Already done' as complete"}
    )

    assert response.status_code == 200

    # Should handle gracefully
    data = response.json()
    assert "response" in data


def test_complete_task_end_to_end_flow(client, test_user, session):
    """Test complete end-to-end flow for task completion"""
    # Step 1: Create a task
    task = Task(user_id=test_user.id, title="Write documentation", is_complete=False)
    session.add(task)
    session.commit()
    session.refresh(task)

    # Step 2: User sends completion message
    user_message = "I finished writing the documentation"

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": user_message}
    )

    assert response.status_code == 200

    # Step 3: Verify response structure
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

    # Step 4: Verify task is complete in database
    session.refresh(task)
    assert task.is_complete is True

    # Step 5: Verify conversation and messages
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

    # Step 6: Verify agent response mentions completion
    response_text = data["response"].lower()
    assert "complete" in response_text or "done" in response_text or "finished" in response_text
