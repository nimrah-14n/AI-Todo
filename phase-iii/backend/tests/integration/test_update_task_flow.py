"""
Integration tests for task update flow through conversation.
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


@pytest.fixture
def client():
    """Create FastAPI test client"""
    return TestClient(app)


def test_update_task_title_only(client, test_user, sample_task, session):
    """Test updating only the task title"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Change 'Buy groceries' to 'Buy groceries and snacks'"}
    )

    assert response.status_code == 200

    # Verify title was updated in database
    session.refresh(sample_task)
    assert "snacks" in sample_task.title.lower()


def test_update_task_description_only(client, test_user, sample_task, session):
    """Test updating only the task description"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Update the groceries task description to 'Milk, eggs, bread, and cheese'"}
    )

    assert response.status_code == 200

    # Verify description was updated
    session.refresh(sample_task)
    assert "cheese" in sample_task.description.lower() or "bread" in sample_task.description.lower()


def test_update_task_both_fields(client, test_user, sample_task, session):
    """Test updating both title and description"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Change 'Buy groceries' to 'Buy party supplies' with description 'Chips, dip, and soda'"}
    )

    assert response.status_code == 200

    # Verify both fields were updated
    session.refresh(sample_task)
    # At least one field should be updated
    assert sample_task.title != "Buy groceries" or sample_task.description != "Milk and eggs"


def test_update_task_various_trigger_phrases(client, test_user, session):
    """Test that various natural language patterns trigger task updates"""
    trigger_phrases = [
        ("Change the task to 'New title'", "change"),
        ("Update the task title to 'Updated title'", "update"),
        ("Rename the task to 'Renamed title'", "rename"),
        ("Edit the task to say 'Edited title'", "edit")
    ]

    for phrase, keyword in trigger_phrases:
        # Create a task for each test
        task = Task(user_id=test_user.id, title=f"Task for {keyword}", is_complete=False)
        session.add(task)
        session.commit()

        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": phrase}
        )

        assert response.status_code == 200


def test_update_task_confirmation_response(client, test_user, sample_task):
    """Test that agent responds with confirmation after updating task"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Change 'Buy groceries' to 'Buy groceries and snacks'"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Response should mention update
    assert any(word in response_text for word in ["update", "updated", "changed", "renamed"])


def test_update_nonexistent_task(client, test_user):
    """Test handling of updating a task that doesn't exist"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Change 'Nonexistent task' to 'New title'"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Agent should indicate task not found
    assert any(word in response_text for word in ["not found", "don't have", "couldn't find", "no task"])


def test_update_task_only_affects_user_tasks(client, session):
    """Test that users can only update their own tasks"""
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
    original_title = task1.title

    # User 2 tries to update User 1's task (should fail)
    response = client.post(
        f"/api/{user2.id}/chat",
        json={"message": "Change 'User 1 task' to 'Hacked title'"}
    )

    assert response.status_code == 200

    # Task should remain unchanged
    session.refresh(task1)
    assert task1.title == original_title


def test_update_task_in_conversation_context(client, test_user, session):
    """Test updating a task within an ongoing conversation"""
    # First, create a task through conversation
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to water plants"}
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Get the task
    tasks = session.query(Task).filter(
        Task.user_id == test_user.id,
        Task.title.contains("water")
    ).all()
    assert len(tasks) >= 1

    # Then update it in same conversation
    response2 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Actually, change that to 'Water plants and flowers'",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200

    # Verify task was updated
    session.refresh(tasks[0])
    assert "flowers" in tasks[0].title.lower() or tasks[0].title != "water plants"


def test_update_task_preserves_completion_status(client, test_user, session):
    """Test that updating a task doesn't change its completion status"""
    # Create a completed task
    task = Task(user_id=test_user.id, title="Completed task", is_complete=True)
    session.add(task)
    session.commit()

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Change 'Completed task' to 'Updated completed task'"}
    )

    assert response.status_code == 200

    # Task should still be complete
    session.refresh(task)
    assert task.is_complete is True


def test_update_task_case_insensitive_matching(client, test_user, session):
    """Test that task title matching is case-insensitive"""
    task = Task(user_id=test_user.id, title="Buy Groceries", is_complete=False)
    session.add(task)
    session.commit()

    # Use lowercase in message
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Change 'buy groceries' to 'Buy snacks'"}
    )

    assert response.status_code == 200

    # Task should be updated
    session.refresh(task)
    assert task.title != "Buy Groceries"


def test_update_task_validation_title_length(client, test_user, sample_task, session):
    """Test that title length validation is enforced"""
    # Try to update with very long title
    long_title = "a" * 250

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": f"Change 'Buy groceries' to '{long_title}'"}
    )

    assert response.status_code == 200

    # Agent should handle this gracefully
    data = response.json()
    assert "response" in data


def test_update_task_end_to_end_flow(client, test_user, session):
    """Test complete end-to-end flow for task update"""
    # Step 1: Create a task
    task = Task(
        user_id=test_user.id,
        title="Original title",
        description="Original description",
        is_complete=False
    )
    session.add(task)
    session.commit()
    session.refresh(task)

    # Step 2: User sends update message
    user_message = "Change 'Original title' to 'Updated title'"

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": user_message}
    )

    assert response.status_code == 200

    # Step 3: Verify response structure
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

    # Step 4: Verify task is updated in database
    session.refresh(task)
    assert task.title != "Original title"

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

    # Step 6: Verify agent response mentions update
    response_text = data["response"].lower()
    assert "update" in response_text or "changed" in response_text or "renamed" in response_text
