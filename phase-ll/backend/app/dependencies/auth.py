"""
Authentication dependency to extract and validate JWT from Authorization header.

[Task]: T020
[From]: specs/001-fullstack-web-app/plan.md, contracts/openapi.yaml
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from uuid import UUID
from app.services.auth import decode_access_token

# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UUID:
    """
    Extract and validate JWT token from Authorization header.
    Returns the authenticated user's ID.

    [Task]: T020

    Args:
        credentials: HTTP Bearer credentials from Authorization header

    Returns:
        User ID (UUID) from validated token

    Raises:
        HTTPException: 401 if token is missing, invalid, or expired
    """
    token = credentials.credentials

    # Decode and validate token
    payload = decode_access_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id_str: Optional[str] = payload.get("sub")

    if user_id_str is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id


async def verify_user_access(
    user_id: UUID,
    path_user_id: UUID,
) -> None:
    """
    Verify that the authenticated user matches the user_id in the URL path.
    Prevents users from accessing other users' resources.

    [Task]: T020, T112

    Args:
        user_id: Authenticated user's ID from JWT token
        path_user_id: User ID from URL path parameter

    Raises:
        HTTPException: 403 if user IDs don't match
    """
    if user_id != path_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
