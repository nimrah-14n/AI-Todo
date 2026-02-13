"""
Integration tests for task deletion flow through conversation.
RED PHASE: These tests should FAIL until the full flow is implemented

Integration tests verify the end-to-end flow:
message → agent → task reference resolution → MCP tool → database deletion
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


def test_delete_task_by_title_reference(client, test_user, sample_tasks, session):
    """Test deleting a task by referencing its title"""
    task_id = sample_tasks[0].id

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete the 'Buy groceries' task"}
    )

    assert response.status_code == 200

    # Verify task was deleted from database
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_various_trigger_phrases(client, test_user, session):
    """Test that various natural language patterns trigger task deletion"""
    trigger_phrases = [
        ("Delete the groceries task", "groceries"),
        ("Remove the task about calling mom", "mom"),
        ("Cancel the report task", "report"),
        ("Get rid of the cleaning task", "cleaning")
    ]

    for phrase, keyword in trigger_phrases:
        # Create a task for each test
        task = Task(user_id=test_user.id, title=f"Task about {keyword}", is_complete=False)
        session.add(task)
        session.commit()
        task_id = task.id

        response = client.post(
            f"/api/{test_user.id}/chat",
            json={"message": phrase}
        )

        assert response.status_code == 200

        # Verify task was deleted
        deleted_task = session.get(Task, task_id)
        assert deleted_task is None


def test_delete_task_confirmation_response(client, test_user, sample_tasks):
    """Test that agent responds with confirmation after deleting task"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete the 'Buy groceries' task"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Response should mention deletion
    assert any(word in response_text for word in ["delete", "removed", "deleted", "cancelled"])

    # Response should mention the task
    assert "groceries" in response_text or "task" in response_text


def test_delete_nonexistent_task(client, test_user):
    """Test handling of deleting a task that doesn't exist"""
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete the 'Nonexistent task'"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Agent should indicate task not found
    assert any(word in response_text for word in ["not found", "don't have", "couldn't find", "no task"])


def test_delete_task_only_affects_user_tasks(client, session):
    """Test that users can only delete their own tasks"""
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
    task1_id = task1.id

    # User 2 tries to delete User 1's task (should fail)
    response = client.post(
        f"/api/{user2.id}/chat",
        json={"message": "Delete 'User 1 task'"}
    )

    assert response.status_code == 200

    # Task should still exist
    task = session.get(Task, task1_id)
    assert task is not None


def test_delete_task_ambiguity_handling(client, test_user, session):
    """Test handling when multiple tasks match the description"""
    # Create multiple tasks with similar titles
    task1 = Task(user_id=test_user.id, title="Buy groceries for Monday", is_complete=False)
    task2 = Task(user_id=test_user.id, title="Buy groceries for Friday", is_complete=False)
    session.add(task1)
    session.add(task2)
    session.commit()

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete the groceries task"}
    )

    assert response.status_code == 200

    data = response.json()
    response_text = data["response"].lower()

    # Agent should either:
    # 1. Ask for clarification
    # 2. Delete one and confirm which one
    # Response should be reasonable
    assert len(response_text) > 0


def test_delete_completed_task(client, test_user, session):
    """Test deleting a task that's already complete"""
    task = Task(user_id=test_user.id, title="Already done", is_complete=True)
    session.add(task)
    session.commit()
    task_id = task.id

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete the 'Already done' task"}
    )

    assert response.status_code == 200

    # Task should be deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_in_conversation_context(client, test_user, session):
    """Test deleting a task within an ongoing conversation"""
    # First, create a task through conversation
    response1 = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Add a task to water plants"}
    )

    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Get the task ID
    tasks = session.query(Task).filter(
        Task.user_id == test_user.id,
        Task.title.contains("water")
    ).all()
    assert len(tasks) >= 1
    task_id = tasks[0].id

    # Then delete it in same conversation
    response2 = client.post(
        f"/api/{test_user.id}/chat",
        json={
            "message": "Actually, delete that watering task",
            "conversation_id": conversation_id
        }
    )

    assert response2.status_code == 200

    # Verify task was deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_preserves_other_tasks(client, test_user, sample_tasks, session):
    """Test that deleting one task doesn't affect others"""
    initial_count = len(sample_tasks)

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete the 'Buy groceries' task"}
    )

    assert response.status_code == 200

    # Count remaining tasks
    remaining_tasks = session.query(Task).filter(Task.user_id == test_user.id).all()

    assert len(remaining_tasks) == initial_count - 1


def test_delete_task_case_insensitive_matching(client, test_user, session):
    """Test that task title matching is case-insensitive"""
    task = Task(user_id=test_user.id, title="Buy Groceries", is_complete=False)
    session.add(task)
    session.commit()
    task_id = task.id

    # Use lowercase in message
    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": "Delete 'buy groceries'"}
    )

    assert response.status_code == 200

    # Task should be deleted
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None


def test_delete_task_end_to_end_flow(client, test_user, session):
    """Test complete end-to-end flow for task deletion"""
    # Step 1: Create a task
    task = Task(user_id=test_user.id, title="Temporary task", is_complete=False)
    session.add(task)
    session.commit()
    task_id = task.id

    # Step 2: User sends deletion message
    user_message = "Delete the 'Temporary task'"

    response = client.post(
        f"/api/{test_user.id}/chat",
        json={"message": user_message}
    )

    assert response.status_code == 200

    # Step 3: Verify response structure
    data = response.json()
    assert "response" in data
    assert "conversation_id" in data

    # Step 4: Verify task is deleted from database
    deleted_task = session.get(Task, task_id)
    assert deleted_task is None

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

    # Step 6: Verify agent response mentions deletion
    response_text = data["response"].lower()
    assert "delete" in response_text or "removed" in response_text or "deleted" in response_text
