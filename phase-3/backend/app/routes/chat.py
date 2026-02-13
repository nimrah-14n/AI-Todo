"""
Chat API endpoint for Todo AI Chatbot.

This module provides the main chat endpoint that handles user messages,
executes the agent, and returns responses.
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from sqlmodel import Session
import logging
import time

from app.database import get_session as get_db
from app.services_chatbot.conversation_service import (
    create_conversation,
    get_latest_conversation,
    load_conversation_history,
    store_message,
    get_conversation
)
from app.agents.todo_agent import TodoAgent
from app.agents.runner import run_agent_with_tools
from app.utils.sanitizer import sanitize_chat_message
from app.utils.metrics import get_metrics

logger = logging.getLogger(__name__)
metrics = get_metrics()

# Create router
router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue existing conversation")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(..., description="Conversation ID for this exchange")


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_db)
) -> ChatResponse:
    """
    Chat endpoint for conversing with the Todo AI assistant.

    This endpoint implements a stateless request-response cycle:
    1. Load or create conversation
    2. Load conversation history
    3. Store user message
    4. Execute agent with history
    5. Store assistant response
    6. Return response

    Args:
        user_id: UUID of the authenticated user
        request: Chat request with message and optional conversation_id
        session: Database session (injected)

    Returns:
        ChatResponse with assistant's response and conversation_id

    Raises:
        HTTPException: If user_id is invalid or processing fails
    """
    start_time = time.time()
    request_id = f"{user_id[:8]}-{int(time.time() * 1000)}"

    logger.info(f"[{request_id}] Chat request started - User: {user_id}, "
               f"Message length: {len(request.message)} chars, "
               f"Conversation ID: {request.conversation_id or 'new'}")

    try:
        # Sanitize user input
        sanitized_message = sanitize_chat_message(request.message)

        if sanitized_message != request.message:
            logger.warning(f"[{request_id}] Message was sanitized")

        # Validate and parse user_id
        try:
            user_uuid = UUID(user_id)
            logger.debug(f"[{request_id}] User ID validated: {user_id}")
        except ValueError:
            logger.warning(f"[{request_id}] Invalid user_id format: {user_id}")
            raise HTTPException(status_code=400, detail="Invalid user_id format")

        # Step 1: Get or create conversation
        if request.conversation_id:
            try:
                conversation_uuid = UUID(request.conversation_id)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid conversation_id format")

            conversation = await get_conversation(conversation_uuid, session)

            if not conversation:
                raise HTTPException(status_code=404, detail="Conversation not found")

            if conversation.user_id != user_uuid:
                raise HTTPException(status_code=403, detail="Conversation does not belong to user")

            logger.info(f"[{request_id}] Using existing conversation: {conversation.id}")
        else:
            conversation = await create_conversation(user_uuid, session)
            logger.info(f"[{request_id}] Created new conversation: {conversation.id}")

        # Step 2: Load conversation history
        history = await load_conversation_history(conversation.id, session)
        logger.info(f"[{request_id}] Loaded {len(history)} messages from history")

        # Step 3: Store user message
        await store_message(
            conversation_id=conversation.id,
            role="user",
            content=sanitized_message,
            session=session
        )

        # Step 4: Execute agent
        agent = TodoAgent(user_id=user_uuid)
        response_text = await run_agent_with_tools(
            agent=agent,
            user_message=sanitized_message,
            conversation_history=history,
            session=session
        )

        # Step 5: Store assistant response
        await store_message(
            conversation_id=conversation.id,
            role="assistant",
            content=response_text,
            session=session
        )

        elapsed_time = time.time() - start_time
        logger.info(f"[{request_id}] Chat request completed in {elapsed_time:.3f}s")

        metrics.record_chat_request(elapsed_time, success=True)

        return ChatResponse(
            response=response_text,
            conversation_id=str(conversation.id)
        )

    except HTTPException:
        raise
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"[{request_id}] Chat request failed after {elapsed_time:.3f}s: {str(e)}", exc_info=True)
        metrics.record_chat_request(elapsed_time, success=False)
        raise HTTPException(status_code=500, detail="Internal server error processing chat request")
