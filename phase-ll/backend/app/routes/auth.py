"""
Authentication routes for signup, signin, and signout.

[Task]: T021, T022, T023
[From]: specs/001-fullstack-web-app/contracts/openapi.yaml
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User
from app.schemas.auth import SignupRequest, SigninRequest, AuthResponse, UserResponse
from app.services.auth import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    request: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Create a new user account.

    [Task]: T021

    Args:
        request: Signup request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token and user information

    Raises:
        HTTPException: 400 if email already registered
    """
    # Normalize email to lowercase
    email = request.email.lower()

    # Check if email already exists
    statement = select(User).where(User.email == email)
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This email is already registered. Please sign in instead.",
        )

    # Hash password
    hashed_password = hash_password(request.password)

    # Create new user
    new_user = User(
        email=email,
        hashed_password=hashed_password
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Generate JWT token
    token = create_access_token(data={"sub": str(new_user.id)})

    # Return response
    return AuthResponse(
        token=token,
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            created_at=new_user.created_at
        )
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    request: SigninRequest,
    session: Session = Depends(get_session)
):
    """
    Sign in to existing account.

    [Task]: T022

    Args:
        request: Signin request with email and password
        session: Database session

    Returns:
        AuthResponse with JWT token and user information

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Normalize email to lowercase
    email = request.email.lower()

    # Find user by email
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    # Verify user exists and password is correct
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Generate JWT token
    token = create_access_token(data={"sub": str(user.id)})

    # Return response
    return AuthResponse(
        token=token,
        user=UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        )
    )


@router.post("/signout")
async def signout():
    """
    Sign out current user.
    Informational endpoint - frontend removes token.

    [Task]: T023

    Returns:
        Success message
    """
    return {"message": "Successfully signed out"}
