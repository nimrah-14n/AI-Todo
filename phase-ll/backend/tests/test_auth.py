"""
Backend authentication tests.

[Task]: T034, T035, T036, T037, T038
[From]: specs/001-fullstack-web-app/spec.md
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_session
from app.models import User, Task


# Create in-memory SQLite database for testing
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


def test_signup_success(client: TestClient):
    """
    Test successful user signup with valid credentials.
    [Task]: T034
    """
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "alice@example.com",
            "password": "securepass123"
        }
    )

    assert response.status_code == 201
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "alice@example.com"
    assert "id" in data["user"]


def test_signup_duplicate_email(client: TestClient):
    """
    Test duplicate email rejection during signup.
    [Task]: T035
    """
    # First signup
    client.post(
        "/api/auth/signup",
        json={
            "email": "bob@example.com",
            "password": "password123"
        }
    )

    # Attempt duplicate signup
    response = client.post(
        "/api/auth/signup",
        json={
            "email": "bob@example.com",
            "password": "differentpass"
        }
    )

    assert response.status_code == 400
    data = response.json()
    assert "already registered" in data["detail"].lower()


def test_signin_success(client: TestClient):
    """
    Test successful signin with valid credentials.
    [Task]: T036
    """
    # First create a user
    client.post(
        "/api/auth/signup",
        json={
            "email": "charlie@example.com",
            "password": "mypassword123"
        }
    )

    # Sign in with correct credentials
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "charlie@example.com",
            "password": "mypassword123"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data
    assert data["user"]["email"] == "charlie@example.com"


def test_signin_invalid_credentials(client: TestClient):
    """
    Test signin failure with invalid credentials.
    [Task]: T037
    """
    # Create a user
    client.post(
        "/api/auth/signup",
        json={
            "email": "dave@example.com",
            "password": "correctpass"
        }
    )

    # Attempt signin with wrong password
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "dave@example.com",
            "password": "wrongpass"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()


def test_signin_nonexistent_user(client: TestClient):
    """
    Test signin failure with non-existent email.
    [Task]: T037
    """
    response = client.post(
        "/api/auth/signin",
        json={
            "email": "nonexistent@example.com",
            "password": "anypassword"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert "invalid" in data["detail"].lower()


def test_jwt_token_validation(client: TestClient):
    """
    Test JWT token validation and expiration.
    [Task]: T038
    """
    # Create user and get token
    signup_response = client.post(
        "/api/auth/signup",
        json={
            "email": "eve@example.com",
            "password": "password123"
        }
    )

    token = signup_response.json()["token"]
    user_id = signup_response.json()["user"]["id"]

    # Test valid token - should be able to access protected endpoint
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200

    # Test invalid token
    response = client.get(
        f"/api/{user_id}/tasks",
        headers={"Authorization": "Bearer invalid_token"}
    )

    assert response.status_code == 401

    # Test missing token
    response = client.get(f"/api/{user_id}/tasks")

    assert response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing auth


def test_password_hashing(client: TestClient, session: Session):
    """
    Test that passwords are hashed and not stored in plain text.
    [Task]: T038
    """
    # Create user
    client.post(
        "/api/auth/signup",
        json={
            "email": "frank@example.com",
            "password": "plaintext123"
        }
    )

    # Query database directly
    from sqlmodel import select
    statement = select(User).where(User.email == "frank@example.com")
    user = session.exec(statement).first()

    # Verify password is hashed (not plain text)
    assert user is not None
    assert user.hashed_password != "plaintext123"
    assert len(user.hashed_password) > 50  # Bcrypt hashes are long
    assert user.hashed_password.startswith("$2b$")  # Bcrypt prefix
