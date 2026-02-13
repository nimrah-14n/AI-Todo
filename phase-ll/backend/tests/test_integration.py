"""
Integration tests for complete user flows.

[Task]: T123, T124
[From]: specs/001-fullstack-web-app/spec.md
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session


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


def test_complete_signup_to_task_completion_flow(client: TestClient):
    """
    Integration test for complete signup → create task → mark complete flow.

    [Task]: T123

    This test verifies the entire user journey:
    1. User signs up
    2. User creates a task
    3. User marks task as complete
    4. User verifies task is complete
    """
    # Step 1: Sign up
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "integration@example.com",
            "password": "testpass123"
        }
    )

    assert signup_response.status_code == 201
    signup_data = signup_response.json()
    token = signup_data["token"]
    user_id = signup_data["user"]["id"]

    # Step 2: Create a task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Complete integration test",
            "description": "This task tests the full flow"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert create_response.status_code == 201
    task_data = create_response.json()
    task_id = task_data["id"]
    assert task_data["is_complete"] is False
    assert task_data["title"] == "Complete integration test"

    # Step 3: Mark task as complete
    complete_response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        json={"is_complete": True},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert complete_response.status_code == 200
    complete_data = complete_response.json()
    assert complete_data["is_complete"] is True

    # Step 4: Verify task is complete by retrieving it
    get_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert get_response.status_code == 200
    retrieved_task = get_response.json()
    assert retrieved_task["is_complete"] is True
    assert retrieved_task["title"] == "Complete integration test"

    # Step 5: Verify task appears in task list as complete
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert list_response.status_code == 200
    list_data = list_response.json()
    assert list_data["count"] == 1
    assert list_data["tasks"][0]["is_complete"] is True


def test_data_isolation_between_two_users(client: TestClient):
    """
    Integration test for data isolation between two users.

    [Task]: T124

    This test verifies that:
    1. Two users can sign up independently
    2. Each user can create their own tasks
    3. Users cannot access each other's tasks
    4. Users cannot modify each other's tasks
    """
    # User 1: Sign up
    user1_signup = client.post(
        "/api/auth/signup",
        json={
            "email": "user1@example.com",
            "password": "pass123"
        }
    )

    assert user1_signup.status_code == 201
    user1_data = user1_signup.json()
    user1_token = user1_data["token"]
    user1_id = user1_data["user"]["id"]

    # User 2: Sign up
    user2_signup = client.post(
        "/api/auth/signup",
        json={
            "email": "user2@example.com",
            "password": "pass456"
        }
    )

    assert user2_signup.status_code == 201
    user2_data = user2_signup.json()
    user2_token = user2_data["token"]
    user2_id = user2_data["user"]["id"]

    # User 1: Create tasks
    user1_task1 = client.post(
        f"/api/{user1_id}/tasks",
        json={"title": "User 1 Task 1"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert user1_task1.status_code == 201
    user1_task1_id = user1_task1.json()["id"]

    user1_task2 = client.post(
        f"/api/{user1_id}/tasks",
        json={"title": "User 1 Task 2"},
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert user1_task2.status_code == 201

    # User 2: Create tasks
    user2_task1 = client.post(
        f"/api/{user2_id}/tasks",
        json={"title": "User 2 Task 1"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert user2_task1.status_code == 201
    user2_task1_id = user2_task1.json()["id"]

    user2_task2 = client.post(
        f"/api/{user2_id}/tasks",
        json={"title": "User 2 Task 2"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert user2_task2.status_code == 201

    # Verify User 1 sees only their own tasks
    user1_list = client.get(
        f"/api/{user1_id}/tasks",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert user1_list.status_code == 200
    user1_tasks = user1_list.json()
    assert user1_tasks["count"] == 2
    assert all(task["user_id"] == user1_id for task in user1_tasks["tasks"])
    assert all("User 1" in task["title"] for task in user1_tasks["tasks"])

    # Verify User 2 sees only their own tasks
    user2_list = client.get(
        f"/api/{user2_id}/tasks",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert user2_list.status_code == 200
    user2_tasks = user2_list.json()
    assert user2_tasks["count"] == 2
    assert all(task["user_id"] == user2_id for task in user2_tasks["tasks"])
    assert all("User 2" in task["title"] for task in user2_tasks["tasks"])

    # User 2 tries to access User 1's tasks - should be forbidden
    forbidden_list = client.get(
        f"/api/{user1_id}/tasks",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert forbidden_list.status_code == 403

    # User 2 tries to access User 1's specific task - should be forbidden
    forbidden_get = client.get(
        f"/api/{user1_id}/tasks/{user1_task1_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert forbidden_get.status_code == 403

    # User 2 tries to modify User 1's task - should be forbidden
    forbidden_update = client.put(
        f"/api/{user1_id}/tasks/{user1_task1_id}",
        json={"title": "Hacked Title"},
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert forbidden_update.status_code == 403

    # User 2 tries to delete User 1's task - should be forbidden
    forbidden_delete = client.delete(
        f"/api/{user1_id}/tasks/{user1_task1_id}",
        headers={"Authorization": f"Bearer {user2_token}"}
    )
    assert forbidden_delete.status_code == 403

    # Verify User 1's task is still intact after User 2's attempts
    verify_task = client.get(
        f"/api/{user1_id}/tasks/{user1_task1_id}",
        headers={"Authorization": f"Bearer {user1_token}"}
    )
    assert verify_task.status_code == 200
    task_data = verify_task.json()
    assert task_data["title"] == "User 1 Task 1"  # Not modified


def test_complete_crud_lifecycle(client: TestClient):
    """
    Integration test for complete CRUD lifecycle of a task.

    Tests: Create → Read → Update → Complete → Delete
    """
    # Sign up
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "crud@example.com",
            "password": "testpass123"
        }
    )

    token = signup_response.json()["token"]
    user_id = signup_response.json()["user"]["id"]

    # CREATE: Create a task
    create_response = client.post(
        f"/api/{user_id}/tasks",
        json={
            "title": "Original Title",
            "description": "Original Description"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert create_response.status_code == 201
    task_id = create_response.json()["id"]

    # READ: Retrieve the task
    read_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert read_response.status_code == 200
    assert read_response.json()["title"] == "Original Title"

    # UPDATE: Modify the task
    update_response = client.put(
        f"/api/{user_id}/tasks/{task_id}",
        json={
            "title": "Updated Title",
            "description": "Updated Description"
        },
        headers={"Authorization": f"Bearer {token}"}
    )

    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Title"

    # COMPLETE: Mark as complete
    complete_response = client.patch(
        f"/api/{user_id}/tasks/{task_id}/complete",
        json={"is_complete": True},
        headers={"Authorization": f"Bearer {token}"}
    )

    assert complete_response.status_code == 200
    assert complete_response.json()["is_complete"] is True

    # DELETE: Remove the task
    delete_response = client.delete(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert delete_response.status_code == 204

    # VERIFY: Task no longer exists
    verify_response = client.get(
        f"/api/{user_id}/tasks/{task_id}",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert verify_response.status_code == 404


def test_multiple_tasks_management(client: TestClient):
    """
    Integration test for managing multiple tasks simultaneously.
    """
    # Sign up
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "multi@example.com",
            "password": "testpass123"
        }
    )

    token = signup_response.json()["token"]
    user_id = signup_response.json()["user"]["id"]

    # Create 5 tasks
    task_ids = []
    for i in range(5):
        response = client.post(
            f"/api/{user_id}/tasks",
            json={"title": f"Task {i+1}"},
            headers={"Authorization": f"Bearer {token}"}
        )
        task_ids.append(response.json()["id"])

    # Verify all tasks exist
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert list_response.json()["count"] == 5

    # Mark some tasks as complete
    for i in [0, 2, 4]:  # Complete tasks 1, 3, 5
        client.patch(
            f"/api/{user_id}/tasks/{task_ids[i]}/complete",
            json={"is_complete": True},
            headers={"Authorization": f"Bearer {token}"}
        )

    # Verify completion status
    list_response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    tasks = list_response.json()["tasks"]
    completed_count = sum(1 for task in tasks if task["is_complete"])
    assert completed_count == 3

    # Delete 2 tasks
    for i in [1, 3]:
        client.delete(
            f"/api/{user_id}/tasks/{task_ids[i]}",
            headers={"Authorization": f"Bearer {token}"}
        )

    # Verify only 3 tasks remain
    final_list = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert final_list.json()["count"] == 3
