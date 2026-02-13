# Research: Todo AI Chatbot Implementation Patterns

**Feature**: Todo AI Chatbot
**Branch**: 001-todo-ai-chatbot
**Date**: 2026-02-07
**Status**: Complete

## Overview

This document captures research findings and implementation patterns for building the Todo AI Chatbot. Since Phase III technologies are mandated by the constitution (OpenAI Agents SDK, MCP Server, ChatKit, FastAPI, Neon PostgreSQL), research focuses on implementation patterns, best practices, and architectural decisions rather than technology selection.

---

## 1. OpenAI Agents SDK Integration Patterns

### Decision: Stateless Agent Architecture with Database-Backed Conversation History

**Rationale**:
- Enables horizontal scaling (any server instance can handle any request)
- Provides resilience (server restarts don't lose conversation state)
- Supports independent request processing (required for stateless architecture)
- Aligns with Phase III constraint: "Server must remain stateless"

**Implementation Pattern**:

```python
from agents import Agent, Runner

# Create fresh agent instance per request (stateless)
def create_todo_agent() -> Agent:
    return Agent(
        name="TodoAssistant",
        instructions="""
        You are a todo management assistant.
        Available tools: add_task, list_tasks, complete_task, delete_task, update_task

        When users say "add", "create" → use add_task
        When users say "show", "list" → use list_tasks
        When users say "done", "complete" → use complete_task
        When users say "delete", "remove" → use delete_task
        When users say "change", "update" → use update_task

        Always confirm actions with friendly responses.
        """,
        model="gpt-4o-mini",
        temperature=0.5
    )

# Execute with full conversation history from database
async def process_message(user_id: str, message: str, conversation_id: int):
    # Load history from database
    history = load_conversation_history(conversation_id)

    # Create fresh agent
    agent = create_todo_agent()

    # Execute with full context
    result = await Runner.run_async(
        agent=agent,
        messages=history + [{"role": "user", "content": message}],
        context_variables={"user_id": user_id}
    )

    # Store response in database
    store_message(conversation_id, "assistant", result.final_output)

    return result
```

**Key Patterns**:
1. **Agent Instructions**: Use explicit trigger patterns ("when users say X → use tool Y")
2. **Temperature**: 0.5 for balanced consistency and natural language flexibility
3. **Context Variables**: Pass user_id to tools for data isolation
4. **Async Execution**: Use `Runner.run_async()` in FastAPI for non-blocking operations
5. **Fresh Instances**: Create new agent per request, no global state

**Alternatives Considered**:
- **Stateful agent with in-memory history**: Rejected - violates stateless architecture requirement, doesn't support horizontal scaling
- **Agent instance pooling**: Rejected - unnecessary complexity for Phase III scale (100 concurrent users)

**Reference**: See `.claude/skills/openai-agent-core/` and `.claude/skills/openai-runner-execution/` for comprehensive implementation examples

---

## 2. MCP Server Implementation

### Decision: Stateless MCP Tools with Direct Database Access

**Rationale**:
- MCP tools must be stateless (mandated by specification FR-020)
- Direct database access in tools simplifies architecture (no service layer needed for Phase III)
- Each tool is independently testable
- Tools can be invoked by agent without server-side state

**Implementation Pattern**:

```python
from mcp.server import Server
from sqlmodel import Session, select

server = Server("todo-mcp-server")

@server.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = None
) -> dict:
    """
    Create a new task.

    Args:
        user_id: User identifier (required)
        title: Task title (required, 1-200 characters)
        description: Task description (optional, max 1000 characters)

    Returns:
        {"task_id": int, "status": "created", "title": str}
    """
    # Validation
    if not title or len(title) > 200:
        raise ValueError("Title must be 1-200 characters")

    # Database operation (stateless)
    with get_session() as session:
        task = Task(user_id=user_id, title=title, description=description)
        session.add(task)
        session.commit()
        session.refresh(task)

        return {
            "task_id": task.id,
            "status": "created",
            "title": task.title
        }
```

**Key Patterns**:
1. **Tool Naming**: Use verb_noun format (add_task, list_tasks)
2. **Validation**: Validate inputs before database operations
3. **Structured Responses**: Return dicts with consistent format (task_id, status, title)
4. **User Isolation**: Always filter by user_id in queries
5. **Error Handling**: Raise exceptions for validation errors, handle gracefully in agent

**Required Tools** (from constitution):
1. `add_task(user_id, title, description?)` → Create task
2. `list_tasks(user_id, status?)` → Get tasks (all/pending/completed)
3. `complete_task(user_id, task_id)` → Mark complete
4. `delete_task(user_id, task_id)` → Remove task
5. `update_task(user_id, task_id, title?, description?)` → Modify task

**Alternatives Considered**:
- **Service layer between tools and database**: Rejected - adds unnecessary complexity for Phase III, violates YAGNI
- **Shared MCP server state**: Rejected - violates stateless requirement
- **Tool result caching**: Rejected - premature optimization, not needed for 100 concurrent users

**Reference**: See `.claude/skills/mcp-server-development/` for complete tool implementations and best practices

---

## 3. ChatKit Frontend Integration

### Decision: OpenAI ChatKit with Optimistic Updates and Domain Allowlist Configuration

**Rationale**:
- ChatKit provides production-ready chat UI (mandated by constitution)
- Optimistic updates improve perceived performance
- Domain allowlist required for production deployment
- Integrates with existing Better Auth from Phase II

**Implementation Pattern**:

```tsx
'use client';

import { ChatKit } from '@openai/chatkit';
import { useState, useEffect } from 'react';
import { useSession } from 'next-auth/react';

export default function ChatPage() {
  const { data: session } = useSession();
  const [messages, setMessages] = useState([]);
  const [conversationId, setConversationId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (message: string) => {
    // Optimistic update
    setMessages(prev => [...prev, { role: 'user', content: message }]);
    setIsLoading(true);

    try {
      const response = await fetch(`/api/${session.user.id}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.accessToken}`
        },
        body: JSON.stringify({ message, conversation_id: conversationId })
      });

      const data = await response.json();

      if (!conversationId) setConversationId(data.conversation_id);

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: data.response
      }]);
    } catch (error) {
      // Rollback optimistic update
      setMessages(prev => prev.slice(0, -1));
      // Show error
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatKit
      messages={messages}
      onSendMessage={handleSendMessage}
      isLoading={isLoading}
      placeholder="Ask me to manage your tasks..."
    />
  );
}
```

**Key Patterns**:
1. **Optimistic Updates**: Add user message immediately, rollback on error
2. **Loading States**: Show typing indicator during API calls
3. **Error Handling**: Graceful failure with user-friendly messages
4. **Authentication**: Use existing Better Auth session
5. **Conversation Persistence**: Store conversation_id, load history on mount

**Domain Allowlist Configuration** (CRITICAL for production):
1. Deploy frontend to get production URL (e.g., Vercel)
2. Add domain to OpenAI allowlist: https://platform.openai.com/settings/organization/security/domain-allowlist
3. Get domain key from OpenAI
4. Add to environment: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-key`

**Alternatives Considered**:
- **Custom chat UI**: Rejected - ChatKit mandated by constitution, provides production-ready features
- **WebSocket for real-time updates**: Rejected - not required for Phase III, adds complexity

**Reference**: See `.claude/skills/chatkit-frontend-integration/` for complete implementation examples

---

## 4. Stateless Architecture Patterns

### Decision: Database-Backed State with Stateless Request-Response Cycle

**Rationale**:
- Mandated by specification (FR-020: "System MUST maintain stateless server architecture")
- Enables horizontal scaling (load balancer can route to any server)
- Provides resilience (server restarts don't lose data)
- Each request is independently processable and testable

**9-Step Stateless Request Cycle** (from Phase III requirements):

```
1. Receive user message
2. Fetch conversation history from database
3. Build message array for agent (history + new message)
4. Store user message in database
5. Run agent with MCP tools
6. Agent invokes appropriate MCP tool(s)
7. Store assistant response in database
8. Return response to client
9. Server holds NO state (ready for next request)
```

**Implementation Pattern**:

```python
@app.post("/api/{user_id}/chat")
async def chat_endpoint(
    user_id: str,
    message: str,
    conversation_id: int = None,
    session: Session = Depends(get_session)
):
    # Step 1: Get or create conversation
    if conversation_id:
        conversation = session.get(Conversation, conversation_id)
    else:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()

    # Step 2: Load history from database
    history = load_conversation_history(conversation.id, session)

    # Step 3: Store user message
    store_message(conversation.id, user_id, "user", message, session)

    # Step 4: Create agent and execute
    agent = create_todo_agent()
    result = await Runner.run_async(
        agent=agent,
        messages=history + [{"role": "user", "content": message}],
        context_variables={"user_id": user_id}
    )

    # Step 5: Store assistant response
    store_message(conversation.id, user_id, "assistant", result.final_output, session)

    # Step 6: Return (server holds no state)
    return {
        "conversation_id": conversation.id,
        "response": result.final_output,
        "tool_calls": [{"tool": c.tool_name, "args": c.arguments} for c in result.tool_calls]
    }
```

**Key Benefits**:
- **Scalability**: Any server instance can handle any request
- **Resilience**: Server restarts don't lose conversations
- **Testability**: Each request is independent and reproducible
- **Horizontal Scaling**: Load balancer can route to any backend

**Alternatives Considered**:
- **In-memory session storage**: Rejected - violates stateless requirement, doesn't support horizontal scaling
- **Redis for session state**: Rejected - adds unnecessary complexity, database is sufficient for Phase III scale

---

## 5. Natural Language Processing Patterns

### Decision: Agent-Based Intent Recognition with Explicit Trigger Patterns

**Rationale**:
- OpenAI Agents SDK handles NLP through agent instructions
- Explicit trigger patterns in instructions improve accuracy
- No need for separate NLP service (YAGNI principle)
- Agent can handle ambiguity through clarifying questions

**Intent Recognition Pattern**:

Agent instructions include explicit mappings:
```
When users say "add", "create", "remember", "I need to" → use add_task
When users say "show", "list", "what", "see", "view" → use list_tasks
When users say "done", "complete", "finished" → use complete_task
When users say "delete", "remove", "cancel" → use delete_task
When users say "change", "update", "rename" → use update_task
```

**Entity Extraction Pattern**:

Agent extracts entities from natural language:
- "Add a task to buy groceries" → title: "Buy groceries"
- "Mark task 3 as complete" → task_id: 3
- "Delete the meeting task" → search for task with "meeting" in title

**Ambiguity Handling Pattern**:

Agent asks clarifying questions when needed:
- Multiple matching tasks → "You have 2 tasks with 'meeting': 1. Team meeting, 2. Client meeting. Which one?"
- Vague request → "Could you clarify which task you mean?"

**Success Criteria**:
- 85%+ intent recognition accuracy (from specification SC-011)
- 90%+ task creation intent accuracy (from specification SC-002)
- 95%+ context maintenance across messages (from specification SC-004)

**Alternatives Considered**:
- **Separate NLP service (spaCy, NLTK)**: Rejected - unnecessary complexity, agent handles NLP through instructions
- **Fine-tuned model for task management**: Rejected - premature optimization, not needed for Phase III

---

## Database Schema Extensions

### New Tables Required

**Conversation Table**:
```sql
CREATE TABLE conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_conversation_user_id ON conversation(user_id);
```

**Message Table**:
```sql
CREATE TABLE message (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES conversation(id),
    user_id UUID NOT NULL REFERENCES users(id),
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_message_conversation_id ON message(conversation_id);
CREATE INDEX idx_message_created_at ON message(created_at);
```

**Rationale**:
- UUID primary keys (per constitution amendment v1.1.0) for security and distributed systems
- Indexes on user_id and conversation_id for query performance
- Role constraint ensures data integrity
- Timestamps for conversation history ordering

---

## Performance Considerations

### Conversation History Pruning

For very long conversations (>100 messages), implement pruning:

```python
def load_conversation_history(conversation_id: int, max_messages: int = 50):
    """Load recent conversation history with pruning."""
    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.desc())
        .limit(max_messages)
    ).all()

    # Reverse to chronological order
    return [{"role": msg.role, "content": msg.content} for msg in reversed(messages)]
```

**Rationale**: Prevents token limit issues, maintains recent context

### Connection Pooling

Configure database connection pool for concurrent requests:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,        # Number of connections to keep open
    max_overflow=20,     # Additional connections when pool is full
    pool_pre_ping=True   # Verify connections before use
)
```

**Rationale**: Supports 100 concurrent users without connection exhaustion

---

## Security Considerations

### User Isolation

All MCP tools and database queries MUST filter by user_id:

```python
# Always filter by user_id
query = select(Task).where(Task.user_id == user_id)

# Validate ownership before modifications
if task.user_id != user_id:
    raise PermissionError("Task belongs to another user")
```

### Authentication

Reuse existing Better Auth from Phase II:
- JWT tokens in Authorization header
- Validate token before processing chat requests
- Extract user_id from validated token

### Input Validation

Validate all inputs before database operations:
- Task titles: 1-200 characters
- Task descriptions: max 1000 characters
- Sanitize user input to prevent injection attacks

---

## Testing Strategy

### Unit Tests
- MCP tool functions (input validation, database operations)
- Agent instruction parsing
- Conversation history loading

### Integration Tests
- Chat endpoint (full request-response cycle)
- Agent + MCP tools integration
- Database persistence

### Contract Tests
- MCP tool schemas
- Chat API OpenAPI specification

### End-to-End Tests
- Complete user workflows (create, view, complete tasks)
- Multi-turn conversations
- Error handling scenarios

---

## Deployment Considerations

### Environment Variables Required

```bash
# Backend
DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
BETTER_AUTH_SECRET=...

# Frontend
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=...
NEXT_PUBLIC_API_URL=...
```

### Production Checklist
- [ ] Domain allowlist configured on OpenAI
- [ ] Database migrations applied
- [ ] Environment variables set
- [ ] MCP server running
- [ ] ChatKit domain key configured
- [ ] Authentication working
- [ ] All tests passing

---

## Summary

All research tasks complete. Key decisions:

1. **OpenAI Agents SDK**: Stateless agent architecture with database-backed conversation history
2. **MCP Server**: Five stateless tools with direct database access
3. **ChatKit**: Optimistic updates with domain allowlist configuration
4. **Architecture**: 9-step stateless request-response cycle
5. **NLP**: Agent-based intent recognition with explicit trigger patterns

**Next Phase**: Generate data-model.md, contracts/, and quickstart.md (Phase 1)
