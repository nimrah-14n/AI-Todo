"""
Conversation service for managing chat conversations and messages.

This module provides functions for creating conversations, loading history,
and storing messages in the database.
"""
from sqlmodel import Session, select
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime
import logging

from ..models.conversation import Conversation
from ..models.message import Message, MessageRole

logger = logging.getLogger(__name__)


async def create_conversation(user_id: UUID, session: Session) -> Conversation:
    """
    Create a new conversation for a user.

    Args:
        user_id: UUID of the user
        session: Database session

    Returns:
        Created Conversation instance
    """
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    logger.info(f"Created conversation {conversation.id} for user {user_id}")

    return conversation


async def get_latest_conversation(user_id: UUID, session: Session) -> Optional[Conversation]:
    """
    Get the user's most recent conversation.

    Args:
        user_id: UUID of the user
        session: Database session

    Returns:
        Most recent Conversation or None if no conversations exist
    """
    statement = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(1)
    )

    conversation = session.exec(statement).first()

    if conversation:
        logger.info(f"Found latest conversation {conversation.id} for user {user_id}")
    else:
        logger.info(f"No conversations found for user {user_id}")

    return conversation


async def load_conversation_history(
    conversation_id: UUID,
    session: Session,
    max_messages: int = 50
) -> List[Dict[str, str]]:
    """
    Load recent messages from a conversation.

    Args:
        conversation_id: UUID of the conversation
        session: Database session
        max_messages: Maximum number of messages to load (default 50)

    Returns:
        List of message dictionaries with 'role' and 'content' keys,
        ordered chronologically (oldest first)
    """
    # Query messages ordered by created_at descending (newest first)
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    )

    messages = session.exec(statement).all()

    # Reverse to chronological order (oldest first)
    messages = list(reversed(messages))

    # Format for agent consumption
    history = [
        {
            "role": msg.role,
            "content": msg.content
        }
        for msg in messages
    ]

    logger.info(f"Loaded {len(history)} messages from conversation {conversation_id}")

    return history


async def store_message(
    conversation_id: UUID,
    user_id: UUID,
    role: str,
    content: str,
    session: Session
) -> Message:
    """
    Store a new message in a conversation.

    Args:
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        role: Message role ('user' or 'assistant')
        content: Message content
        session: Database session

    Returns:
        Created Message instance

    Raises:
        ValueError: If role is invalid or content is empty
    """
    # Validate role
    if role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
        raise ValueError(f"Invalid role: {role}. Must be 'user' or 'assistant'")

    # Validate content
    if not content or not content.strip():
        raise ValueError("Message content cannot be empty")

    # Create message
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        role=role,
        content=content.strip()
    )

    session.add(message)

    # Update conversation timestamp
    conversation = session.get(Conversation, conversation_id)
    if conversation:
        conversation.updated_at = datetime.utcnow()
        session.add(conversation)

    session.commit()
    session.refresh(message)

    logger.info(f"Stored {role} message in conversation {conversation_id}")

    return message


async def get_conversation(conversation_id: UUID, session: Session) -> Optional[Conversation]:
    """
    Get a conversation by ID.

    Args:
        conversation_id: UUID of the conversation
        session: Database session

    Returns:
        Conversation instance or None if not found
    """
    conversation = session.get(Conversation, conversation_id)

    if conversation:
        logger.info(f"Found conversation {conversation_id}")
    else:
        logger.info(f"Conversation {conversation_id} not found")

    return conversation


async def prune_conversation_history(
    conversation_id: UUID,
    session: Session,
    max_messages: int = 100
) -> int:
    """
    Prune old messages from a conversation to keep it under the maximum limit.

    This function keeps the most recent messages and deletes older ones.
    Useful for preventing conversations from growing indefinitely.

    Args:
        conversation_id: UUID of the conversation
        session: Database session
        max_messages: Maximum number of messages to keep (default 100)

    Returns:
        Number of messages deleted

    Raises:
        ValueError: If max_messages is less than 1
    """
    if max_messages < 1:
        raise ValueError("max_messages must be at least 1")

    try:
        # Count total messages in conversation
        count_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
        )
        all_messages = session.exec(count_statement).all()
        total_messages = len(all_messages)

        if total_messages <= max_messages:
            logger.debug(f"Conversation {conversation_id} has {total_messages} messages, "
                        f"no pruning needed (max: {max_messages})")
            return 0

        # Calculate how many messages to delete
        messages_to_delete = total_messages - max_messages

        # Get the oldest messages to delete
        delete_statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .limit(messages_to_delete)
        )
        messages_to_remove = session.exec(delete_statement).all()

        # Delete the messages
        deleted_count = 0
        for message in messages_to_remove:
            session.delete(message)
            deleted_count += 1

        session.commit()

        logger.info(f"Pruned {deleted_count} old messages from conversation {conversation_id} "
                   f"(had {total_messages}, now has {total_messages - deleted_count})")

        return deleted_count

    except Exception as e:
        session.rollback()
        logger.error(f"Error pruning conversation {conversation_id}: {str(e)}", exc_info=True)
        raise


async def get_conversation_message_count(
    conversation_id: UUID,
    session: Session
) -> int:
    """
    Get the total number of messages in a conversation.

    Args:
        conversation_id: UUID of the conversation
        session: Database session

    Returns:
        Number of messages in the conversation
    """
    statement = (
        select(Message)
        .where(Message.conversation_id == conversation_id)
    )
    messages = session.exec(statement).all()
    count = len(messages)

    logger.debug(f"Conversation {conversation_id} has {count} messages")

    return count
