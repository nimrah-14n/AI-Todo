"""
Input sanitization utilities for security.

This module provides functions to sanitize user inputs to prevent
XSS attacks, SQL injection, and other security vulnerabilities.
"""
import re
import html
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class InputSanitizer:
    """
    Input sanitization utilities for user-provided data.
    """

    # Patterns for detecting potentially malicious content
    SCRIPT_PATTERN = re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL)
    HTML_TAG_PATTERN = re.compile(r'<[^>]+>')
    SQL_INJECTION_PATTERN = re.compile(
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        re.IGNORECASE
    )

    @staticmethod
    def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
        """
        Sanitize text input by removing HTML tags and escaping special characters.

        Args:
            text: Input text to sanitize
            max_length: Optional maximum length to truncate to

        Returns:
            Sanitized text
        """
        if not text:
            return ""

        # Strip leading/trailing whitespace
        sanitized = text.strip()

        # Remove script tags
        sanitized = InputSanitizer.SCRIPT_PATTERN.sub('', sanitized)

        # Remove HTML tags
        sanitized = InputSanitizer.HTML_TAG_PATTERN.sub('', sanitized)

        # Escape HTML entities
        sanitized = html.escape(sanitized)

        # Truncate if max_length specified
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Text truncated from {len(text)} to {max_length} characters")

        # Log if suspicious content was detected
        if sanitized != text.strip():
            logger.warning(f"Suspicious content detected and sanitized: "
                         f"Original length: {len(text)}, Sanitized length: {len(sanitized)}")

        return sanitized

    @staticmethod
    def sanitize_task_title(title: str) -> str:
        """
        Sanitize task title input.

        Args:
            title: Task title to sanitize

        Returns:
            Sanitized task title (max 200 characters)
        """
        return InputSanitizer.sanitize_text(title, max_length=200)

    @staticmethod
    def sanitize_task_description(description: Optional[str]) -> Optional[str]:
        """
        Sanitize task description input.

        Args:
            description: Task description to sanitize

        Returns:
            Sanitized task description (max 1000 characters) or None
        """
        if not description:
            return None

        return InputSanitizer.sanitize_text(description, max_length=1000)

    @staticmethod
    def sanitize_chat_message(message: str) -> str:
        """
        Sanitize chat message input.

        Args:
            message: Chat message to sanitize

        Returns:
            Sanitized chat message (max 5000 characters)
        """
        return InputSanitizer.sanitize_text(message, max_length=5000)

    @staticmethod
    def detect_sql_injection(text: str) -> bool:
        """
        Detect potential SQL injection attempts.

        Note: This is a basic check. SQLModel ORM provides primary protection.

        Args:
            text: Text to check

        Returns:
            True if potential SQL injection detected, False otherwise
        """
        if InputSanitizer.SQL_INJECTION_PATTERN.search(text):
            logger.warning(f"Potential SQL injection detected in input: {text[:100]}")
            return True
        return False

    @staticmethod
    def validate_uuid_format(uuid_str: str) -> bool:
        """
        Validate UUID format.

        Args:
            uuid_str: UUID string to validate

        Returns:
            True if valid UUID format, False otherwise
        """
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(uuid_str))

    @staticmethod
    def sanitize_and_validate(
        text: str,
        field_name: str,
        max_length: int,
        allow_empty: bool = False
    ) -> str:
        """
        Sanitize and validate text input with comprehensive checks.

        Args:
            text: Input text to sanitize
            field_name: Name of the field (for logging)
            max_length: Maximum allowed length
            allow_empty: Whether empty strings are allowed

        Returns:
            Sanitized text

        Raises:
            ValueError: If validation fails
        """
        # Check for None
        if text is None:
            if allow_empty:
                return ""
            raise ValueError(f"{field_name} cannot be None")

        # Sanitize
        sanitized = InputSanitizer.sanitize_text(text, max_length=max_length)

        # Check if empty after sanitization
        if not sanitized and not allow_empty:
            logger.warning(f"{field_name} is empty after sanitization")
            raise ValueError(f"{field_name} cannot be empty")

        # Check length
        if len(sanitized) > max_length:
            raise ValueError(f"{field_name} must be {max_length} characters or less")

        # Check for SQL injection attempts
        if InputSanitizer.detect_sql_injection(sanitized):
            raise ValueError(f"{field_name} contains invalid content")

        logger.debug(f"Sanitized and validated {field_name}: {len(sanitized)} chars")

        return sanitized


# Convenience functions
def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """Sanitize general text input."""
    return InputSanitizer.sanitize_text(text, max_length)


def sanitize_task_title(title: str) -> str:
    """Sanitize task title."""
    return InputSanitizer.sanitize_task_title(title)


def sanitize_task_description(description: Optional[str]) -> Optional[str]:
    """Sanitize task description."""
    return InputSanitizer.sanitize_task_description(description)


def sanitize_chat_message(message: str) -> str:
    """Sanitize chat message."""
    return InputSanitizer.sanitize_chat_message(message)
