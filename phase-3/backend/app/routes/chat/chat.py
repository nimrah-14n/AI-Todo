"""
Chat API endpoint for Todo AI Chatbot.

This module provides the main chat endpoint that handles user messages,
executes the agent, and returns responses.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from sqlmodel import Session
import logging
import time

from ..mcp.database import get_session
from ..services.conversation_service import (
    create_conversation,
    get_latest_conversation,
    load_conversation_history,
    store_message,
    get_conversation
)
from ..agents.todo_agent import TodoAgent
from ..agents.runner import run_agent_with_tools
# Temporarily disabled for testing:
# from .auth import validate_user_access
# from .rate_limiter import check_rate_limit
from ..utils.sanitizer import sanitize_chat_message
from ..utils.metrics import get_metrics

logger = logging.getLogger(__name__)
metrics = get_metrics()

# Initialize FastAPI app
app = FastAPI(title="Todo AI Chatbot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: Optional[str] = Field(None, description="Optional conversation ID to continue existing conversation")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(..., description="Conversation ID for this exchange")


@app.post("/api/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session)
    # Temporarily disabled for testing:
    # _: None = Depends(validate_user_access),
    # __: None = Depends(lambda: check_rate_limit(user_id))
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
            logger.warning(f"[{request_id}] Message was sanitized - "
                         f"Original: {len(request.message)} chars, "
                         f"Sanitized: {len(sanitized_message)} chars")

        # Validate and parse user_id
        try:
            user_uuid = UUID(user_id)
            logger.debug(f"[{request_id}] User ID validated: {user_id}")
        except ValueError:
            logger.warning(f"[{request_id}] Invalid user_id format: {user_id}")
            raise HTTPException(status_code=400, detail="Invalid user_id format")

        # Step 1: Get or create conversation
        step_start = time.time()
        if request.conversation_id:
            # Use existing conversation
            try:
                conversation_uuid = UUID(request.conversation_id)
            except ValueError:
                logger.warning(f"[{request_id}] Invalid conversation_id format: {request.conversation_id}")
                raise HTTPException(status_code=400, detail="Invalid conversation_id format")

            conversation = await get_conversation(conversation_uuid, session)

            if not conversation:
                logger.warning(f"[{request_id}] Conversation not found: {request.conversation_id}")
                raise HTTPException(status_code=404, detail="Conversation not found")

            if conversation.user_id != user_uuid:
                logger.warning(f"[{request_id}] Access denied - Conversation {request.conversation_id} "
                             f"belongs to different user")
                raise HTTPException(status_code=403, detail="Conversation does not belong to user")

            logger.info(f"[{request_id}] Using existing conversation: {conversation.id}")
        else:
            # Create new conversation
            conversation = await create_conversation(user_uuid, session)
            logger.info(f"[{request_id}] Created new conversation: {conversation.id}")

        step_time = time.time() - step_start
        logger.debug(f"[{request_id}] Step 1 (Get/Create conversation) completed in {step_time:.3f}s")

        # Step 2: Load conversation history
        step_start = time.time()
        history = await load_conversation_history(conversation.id, session)
        step_time = time.time() - step_start

        logger.info(f"[{request_id}] Loaded {len(history)} messages from history in {step_time:.3f}s")

        # Step 3: Store user message
        step_start = time.time()
        await store_message(
            conversation_id=conversation.id,
            user_id=user_uuid,
            role="user",
            content=sanitized_message,
            session=session
        )
        step_time = time.time() - step_start
        logger.debug(f"[{request_id}] Step 3 (Store user message) completed in {step_time:.3f}s")

        # Step 4: Execute agent with history
        step_start = time.time()
        agent = TodoAgent()
        agent_config = agent.get_config()

        logger.info(f"[{request_id}] Executing agent with model: {agent_config.get('model', 'unknown')}")

        assistant_response = await run_agent_with_tools(
            user_message=sanitized_message,
            conversation_history=history,
            agent_config=agent_config,
            user_id=user_id,
            session=session
        )
        step_time = time.time() - step_start

        logger.info(f"[{request_id}] Agent execution completed in {step_time:.3f}s - "
                   f"Response length: {len(assistant_response)} chars")

        # Step 5: Store assistant response
        step_start = time.time()
        await store_message(
            conversation_id=conversation.id,
            user_id=user_uuid,
            role="assistant",
            content=assistant_response,
            session=session
        )
        step_time = time.time() - step_start
        logger.debug(f"[{request_id}] Step 5 (Store assistant response) completed in {step_time:.3f}s")

        # Step 6: Return response
        total_time = time.time() - start_time

        # Record metrics
        metrics.record_request(duration=total_time, success=True)
        metrics.record_conversation_created() if not request.conversation_id else None
        metrics.record_message_stored()  # User message
        metrics.record_message_stored()  # Assistant message

        logger.info(f"[{request_id}] Chat request completed successfully in {total_time:.3f}s")

        return ChatResponse(
            response=assistant_response,
            conversation_id=str(conversation.id)
        )

    except HTTPException as e:
        total_time = time.time() - start_time

        # Record metrics
        metrics.record_request(duration=total_time, success=False)
        metrics.record_error(f"HTTP_{e.status_code}")

        if e.status_code == 429:
            metrics.record_rate_limit_hit()

        logger.warning(f"[{request_id}] Chat request failed with HTTP {e.status_code} "
                      f"after {total_time:.3f}s: {e.detail}")
        raise
    except Exception as e:
        total_time = time.time() - start_time

        # Record metrics
        metrics.record_request(duration=total_time, success=False)
        metrics.record_error("INTERNAL_ERROR")

        logger.error(f"[{request_id}] Chat request failed with unexpected error "
                    f"after {total_time:.3f}s: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/{user_id}/conversations")
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session)
    # Temporarily disabled for testing:
    # _: None = Depends(validate_user_access)
):
    """
    List all conversations for a user.

    Returns conversations ordered by most recent first (updated_at DESC).

    Args:
        user_id: UUID of the authenticated user
        session: Database session (injected)

    Returns:
        List of conversations with metadata

    Raises:
        HTTPException: If user_id is invalid
    """
    try:
        # Validate and parse user_id
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid user_id format")

        # Get all conversations for user, ordered by most recent
        from sqlmodel import select
        from ..models.conversation import Conversation

        statement = (
            select(Conversation)
            .where(Conversation.user_id == user_uuid)
            .order_by(Conversation.updated_at.desc())
        )

        conversations = session.exec(statement).all()

        # Format response
        conversation_list = [
            {
                "id": str(conv.id),
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat()
            }
            for conv in conversations
        ]

        return {"conversations": conversation_list}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List conversations error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/{user_id}/conversations/{conversation_id}")
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session)
    # Temporarily disabled for testing:
    # _: None = Depends(validate_user_access)
):
    """
    Get conversation history with messages.

    Returns up to 50 most recent messages in chronological order.

    Args:
        user_id: UUID of the authenticated user
        conversation_id: UUID of the conversation
        session: Database session (injected)

    Returns:
        Conversation with messages

    Raises:
        HTTPException: If conversation not found or access denied
    """
    try:
        # Validate and parse IDs
        try:
            user_uuid = UUID(user_id)
            conv_uuid = UUID(conversation_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid ID format")

        # Get conversation
        conversation = await get_conversation(conv_uuid, session)

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Verify ownership
        if conversation.user_id != user_uuid:
            raise HTTPException(status_code=403, detail="Access denied")

        # Load conversation history (limited to 50 messages)
        history = await load_conversation_history(conv_uuid, session, max_messages=50)

        return {
            "id": str(conversation.id),
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat(),
            "messages": history
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation history error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
