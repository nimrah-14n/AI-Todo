"""
Backend task CRUD tests.

[Task]: T055, T056, T057, T058, T059, T060, T073, T074, T075, T076, T088, T089, T090, T091, T092, T103, T104, T105, T106
[From]: specs/001-fullstack-web-app/spec.md
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models import User, Task


@pytest.fixture(name="session")
def session_fixture():
    """Create a fresh database session for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    """Create a test client with overridden database session."""
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="auth_user")
def auth_user_fixture(client: TestClient):
    """Create and authenticate a test user."""
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "testuser@example.com",
            "password": "testpass123"
        }
    )
    data = response.json()
    return {
        "token": data["token"],
        "user_id": data["user"]["id"],
        "email": data["user"]["email"]
    }


# Task Creation Tests (T055-T058)

def test_create_task_with_title_and_description(client: TestClient, auth_user: dict):
    """
    Test creating task with valid title and description.
    [Task]: T055
    """
    response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={
            "title": "Buy groceries",
            "description": "Milk, eggs, bread"
        },
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy groceries"
    assert data["description"] == "Milk, eggs, bread"
    assert data["is_complete"] is False
    assert data["user_id"] == auth_user["user_id"]


def test_create_task_with_only_title(client: TestClient, auth_user: dict):
    """
    Test creating task with only title (no description).
    [Task]: T056
    """
    response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={
            "title": "Call dentist"
        },
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Call dentist"
    assert data["description"] is None
    assert data["is_complete"] is False


def test_reject_task_with_empty_title(client: TestClient, auth_user: dict):
    """
    Test rejecting task with empty title.
    [Task]: T057
    """
    response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={
            "title": "",
            "description": "Some description"
        },
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 422  # Validation error


def test_reject_task_with_title_exceeding_200_chars(client: TestClient, auth_user: dict):
    """
    Test rejecting task with title exceeding 200 characters.
    [Task]: T058
    """
    long_title = "A" * 201

    response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={
            "title": long_title,
            "description": "Description"
        },
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 422  # Validation error


# Task Retrieval Tests (T059-T060)

def test_retrieve_all_tasks_for_user(client: TestClient, auth_user: dict):
    """
    Test retrieving all tasks for authenticated user.
    [Task]: T059
    """
    # Create multiple tasks
    client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Task 1"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Task 2"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    # Retrieve all tasks
    response = client.get(
        f"/api/{auth_user['user_id']}/tasks",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert len(data["tasks"]) == 2


def test_data_isolation_between_users(client: TestClient, auth_user: dict):
    """
    Test that user cannot see other user's tasks.
    [Task]: T060
    """
    # Create second user
    user2_response = client.post(
        "/api/auth/signup",
        json={
            "email": "user2@example.com",
            "password": "pass123"
        }
    )
    user2_data = user2_response.json()

    # User 1 creates a task
    client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    # User 2 creates a task
    client.post(
        f"/api/{user2_data['user']['id']}/tasks",
        json={"title": "User 2 Task"},
        headers={"Authorization": f"Bearer {user2_data['token']}"}
    )

    # User 1 retrieves tasks - should only see their own
    response = client.get(
        f"/api/{auth_user['user_id']}/tasks",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    data = response.json()
    assert data["count"] == 1
    assert data["tasks"][0]["title"] == "User 1 Task"

    # User 2 tries to access User 1's tasks - should be forbidden
    response = client.get(
        f"/api/{auth_user['user_id']}/tasks",
        headers={"Authorization": f"Bearer {user2_data['token']}"}
    )

    assert response.status_code == 403


# Task Completion Tests (T073-T076)

def test_mark_incomplete_task_as_complete(client: TestClient, auth_user: dict):
    """
    Test marking incomplete task as complete.
    [Task]: T073
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Mark as complete
    response = client.patch(
        f"/api/{auth_user['user_id']}/tasks/{task_id}/complete",
        json={"is_complete": True},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_complete"] is True


def test_mark_complete_task_as_incomplete(client: TestClient, auth_user: dict):
    """
    Test marking complete task as incomplete.
    [Task]: T074
    """
    # Create and complete task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    client.patch(
        f"/api/{auth_user['user_id']}/tasks/{task_id}/complete",
        json={"is_complete": True},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    # Mark as incomplete
    response = client.patch(
        f"/api/{auth_user['user_id']}/tasks/{task_id}/complete",
        json={"is_complete": False},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_complete"] is False


def test_completion_status_persistence(client: TestClient, auth_user: dict):
    """
    Test completion status persists across requests.
    [Task]: T075
    """
    # Create and complete task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Test Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    client.patch(
        f"/api/{auth_user['user_id']}/tasks/{task_id}/complete",
        json={"is_complete": True},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    # Retrieve task again
    response = client.get(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["is_complete"] is True


def test_ownership_check_on_completion_toggle(client: TestClient, auth_user: dict):
    """
    Test ownership check on completion toggle.
    [Task]: T076
    """
    # Create second user
    user2_response = client.post(
        "/api/auth/signup",
        json={"email": "user2@example.com", "password": "pass123"}
    )
    user2_data = user2_response.json()

    # User 1 creates task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # User 2 tries to toggle User 1's task - should fail
    response = client.patch(
        f"/api/{auth_user['user_id']}/tasks/{task_id}/complete",
        json={"is_complete": True},
        headers={"Authorization": f"Bearer {user2_data['token']}"}
    )

    assert response.status_code == 403


# Task Update Tests (T088-T092)

def test_update_task_title_only(client: TestClient, auth_user: dict):
    """
    Test updating task title only.
    [Task]: T088
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Original Title", "description": "Original Description"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Update title
    response = client.put(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        json={"title": "Updated Title", "description": "Original Description"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Updated Title"
    assert data["description"] == "Original Description"


def test_update_task_description_only(client: TestClient, auth_user: dict):
    """
    Test updating task description only.
    [Task]: T089
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Title", "description": "Original"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Update description
    response = client.put(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        json={"title": "Title", "description": "Updated Description"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated Description"


def test_update_both_title_and_description(client: TestClient, auth_user: dict):
    """
    Test updating both title and description.
    [Task]: T090
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Old Title", "description": "Old Description"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Update both
    response = client.put(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        json={"title": "New Title", "description": "New Description"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "New Title"
    assert data["description"] == "New Description"


def test_reject_update_with_empty_title(client: TestClient, auth_user: dict):
    """
    Test rejecting update with empty title.
    [Task]: T091
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Valid Title"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Try to update with empty title
    response = client.put(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        json={"title": ""},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 422


def test_ownership_check_on_task_update(client: TestClient, auth_user: dict):
    """
    Test ownership check on task update.
    [Task]: T092
    """
    # Create second user
    user2_response = client.post(
        "/api/auth/signup",
        json={"email": "user2@example.com", "password": "pass123"}
    )
    user2_data = user2_response.json()

    # User 1 creates task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # User 2 tries to update User 1's task
    response = client.put(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {user2_data['token']}"}
    )

    assert response.status_code == 403


# Task Delete Tests (T103-T106)

def test_successful_task_deletion(client: TestClient, auth_user: dict):
    """
    Test successful task deletion.
    [Task]: T103
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Task to Delete"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Delete task
    response = client.delete(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 204


def test_deletion_persistence(client: TestClient, auth_user: dict):
    """
    Test task not retrievable after delete.
    [Task]: T104
    """
    # Create task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "Task to Delete"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # Delete task
    client.delete(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    # Try to retrieve deleted task
    response = client.get(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 404


def test_ownership_check_on_task_deletion(client: TestClient, auth_user: dict):
    """
    Test ownership check on task deletion.
    [Task]: T105
    """
    # Create second user
    user2_response = client.post(
        "/api/auth/signup",
        json={"email": "user2@example.com", "password": "pass123"}
    )
    user2_data = user2_response.json()

    # User 1 creates task
    create_response = client.post(
        f"/api/{auth_user['user_id']}/tasks",
        json={"title": "User 1 Task"},
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )
    task_id = create_response.json()["id"]

    # User 2 tries to delete User 1's task
    response = client.delete(
        f"/api/{auth_user['user_id']}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {user2_data['token']}"}
    )

    assert response.status_code == 403


def test_404_when_deleting_nonexistent_task(client: TestClient, auth_user: dict):
    """
    Test 404 error when deleting non-existent task.
    [Task]: T106
    """
    fake_task_id = "00000000-0000-0000-0000-000000000000"

    response = client.delete(
        f"/api/{auth_user['user_id']}/tasks/{fake_task_id}",
        headers={"Authorization": f"Bearer {auth_user['token']}"}
    )

    assert response.status_code == 404
