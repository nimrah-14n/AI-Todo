"""
Authentication middleware for validating JWT tokens.

This module provides middleware to validate authentication tokens
and extract user information from requests.
"""
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
import jwt
import os
import logging

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# Get secret from environment
JWT_SECRET = os.getenv("BETTER_AUTH_SECRET")

if not JWT_SECRET:
    logger.warning("BETTER_AUTH_SECRET not set - authentication will fail")


def verify_token(token: str) -> dict:
    """
    Verify JWT token and extract payload.

    Args:
        token: JWT token string

    Returns:
        Token payload dictionary

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"]
        )

        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """
    Dependency to get current authenticated user from token.

    Args:
        credentials: HTTP authorization credentials

    Returns:
        User information dictionary with 'user_id' key

    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials

    # Verify token
    payload = verify_token(token)

    # Extract user_id from payload
    user_id = payload.get("user_id") or payload.get("sub")

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    # Validate user_id format
    try:
        UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user_id in token")

    logger.info(f"Authenticated user: {user_id}")

    return {
        "user_id": user_id,
        "payload": payload
    }


async def validate_user_access(
    user_id: str,
    current_user: dict = Depends(get_current_user)
) -> None:
    """
    Validate that the authenticated user matches the requested user_id.

    This prevents users from accessing other users' data.

    Args:
        user_id: Requested user_id from path parameter
        current_user: Current authenticated user from token

    Raises:
        HTTPException: If user_id doesn't match authenticated user
    """
    if current_user["user_id"] != user_id:
        logger.warning(
            f"User {current_user['user_id']} attempted to access "
            f"resources for user {user_id}"
        )
        raise HTTPException(
            status_code=403,
            detail="Access denied: Cannot access other users' data"
        )


# Optional: For development/testing without authentication
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security, auto_error=False)
) -> Optional[dict]:
    """
    Optional authentication dependency for development.

    Returns None if no credentials provided instead of raising error.

    Args:
        credentials: Optional HTTP authorization credentials

    Returns:
        User information dictionary or None
    """
    if not credentials:
        return None

    return await get_current_user(credentials)
