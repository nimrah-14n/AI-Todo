"""
Rate limiting middleware for API endpoints.

This module provides rate limiting functionality to prevent abuse
and ensure fair usage of the API.
"""
from fastapi import HTTPException, Request
from typing import Dict, Tuple
from datetime import datetime, timedelta
import logging
from collections import defaultdict
import asyncio

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Simple in-memory rate limiter using sliding window algorithm.

    For production, consider using Redis for distributed rate limiting.
    """

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute per user
            requests_per_hour: Maximum requests per hour per user
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Store request timestamps: {user_id: [timestamp1, timestamp2, ...]}
        self.request_history: Dict[str, list] = defaultdict(list)

        # Lock for thread-safe operations
        self.lock = asyncio.Lock()

        logger.info(f"Rate limiter initialized - "
                   f"{requests_per_minute} req/min, {requests_per_hour} req/hour")

    async def check_rate_limit(self, user_id: str) -> Tuple[bool, str]:
        """
        Check if user has exceeded rate limits.

        Args:
            user_id: UUID of the user

        Returns:
            Tuple of (is_allowed, error_message)
            - is_allowed: True if request is allowed, False if rate limited
            - error_message: Error message if rate limited, empty string otherwise
        """
        async with self.lock:
            now = datetime.utcnow()

            # Get user's request history
            timestamps = self.request_history[user_id]

            # Remove timestamps older than 1 hour
            one_hour_ago = now - timedelta(hours=1)
            timestamps = [ts for ts in timestamps if ts > one_hour_ago]

            # Check hourly limit
            if len(timestamps) >= self.requests_per_hour:
                logger.warning(f"Rate limit exceeded (hourly) for user {user_id}: "
                             f"{len(timestamps)} requests in last hour")
                return False, f"Rate limit exceeded: {self.requests_per_hour} requests per hour"

            # Check per-minute limit
            one_minute_ago = now - timedelta(minutes=1)
            recent_requests = [ts for ts in timestamps if ts > one_minute_ago]

            if len(recent_requests) >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded (per-minute) for user {user_id}: "
                             f"{len(recent_requests)} requests in last minute")
                return False, f"Rate limit exceeded: {self.requests_per_minute} requests per minute"

            # Add current timestamp
            timestamps.append(now)
            self.request_history[user_id] = timestamps

            logger.debug(f"Rate limit check passed for user {user_id}: "
                        f"{len(recent_requests)}/{self.requests_per_minute} per minute, "
                        f"{len(timestamps)}/{self.requests_per_hour} per hour")

            return True, ""

    async def cleanup_old_entries(self):
        """
        Clean up old entries from request history.

        Should be called periodically to prevent memory growth.
        """
        async with self.lock:
            now = datetime.utcnow()
            one_hour_ago = now - timedelta(hours=1)

            # Remove old timestamps and empty user entries
            users_to_remove = []

            for user_id, timestamps in self.request_history.items():
                # Filter out old timestamps
                recent_timestamps = [ts for ts in timestamps if ts > one_hour_ago]

                if recent_timestamps:
                    self.request_history[user_id] = recent_timestamps
                else:
                    users_to_remove.append(user_id)

            # Remove users with no recent requests
            for user_id in users_to_remove:
                del self.request_history[user_id]

            logger.info(f"Rate limiter cleanup completed - "
                       f"Active users: {len(self.request_history)}, "
                       f"Removed: {len(users_to_remove)}")

    def get_stats(self, user_id: str) -> Dict[str, int]:
        """
        Get rate limit statistics for a user.

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with request counts
        """
        now = datetime.utcnow()
        timestamps = self.request_history.get(user_id, [])

        one_minute_ago = now - timedelta(minutes=1)
        one_hour_ago = now - timedelta(hours=1)

        recent_minute = len([ts for ts in timestamps if ts > one_minute_ago])
        recent_hour = len([ts for ts in timestamps if ts > one_hour_ago])

        return {
            "requests_last_minute": recent_minute,
            "requests_last_hour": recent_hour,
            "limit_per_minute": self.requests_per_minute,
            "limit_per_hour": self.requests_per_hour,
            "remaining_minute": max(0, self.requests_per_minute - recent_minute),
            "remaining_hour": max(0, self.requests_per_hour - recent_hour)
        }


# Global rate limiter instance
# For production, configure limits via environment variables
rate_limiter = RateLimiter(
    requests_per_minute=60,  # 60 requests per minute
    requests_per_hour=1000   # 1000 requests per hour
)


async def check_rate_limit(user_id: str):
    """
    Dependency function to check rate limits.

    Args:
        user_id: UUID of the user

    Raises:
        HTTPException: If rate limit is exceeded
    """
    is_allowed, error_message = await rate_limiter.check_rate_limit(user_id)

    if not is_allowed:
        logger.warning(f"Rate limit exceeded for user {user_id}")
        raise HTTPException(
            status_code=429,
            detail=error_message,
            headers={"Retry-After": "60"}
        )
