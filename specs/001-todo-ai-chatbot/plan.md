# Implementation Plan: Todo AI Chatbot

**Branch**: `001-todo-ai-chatbot` | **Date**: 2026-02-07 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-todo-ai-chatbot/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build an AI-powered conversational interface for managing todo tasks through natural language. Users interact with a chatbot that understands commands like "Add a task to buy groceries" and executes task operations (create, view, complete, delete, update) through an MCP server architecture. The system uses OpenAI Agents SDK for AI logic, maintains stateless server architecture with database-backed conversation state, and provides a ChatKit-based frontend for the chat interface.

**Core Technical Approach**:
- **Frontend**: OpenAI ChatKit component in Next.js for chat UI
- **Backend**: FastAPI endpoint that receives messages, loads conversation history from database, executes OpenAI Agent with MCP tools, stores responses
- **MCP Server**: Five stateless tools (add_task, list_tasks, complete_task, delete_task, update_task) that interact with database
- **State Management**: All conversation and message history stored in PostgreSQL (Neon), no server-side session state
- **AI Integration**: OpenAI Agents SDK with Runner for agent execution, context variables for user identification

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/Next.js 16+ (frontend)
**Primary Dependencies**:
- Backend: FastAPI, OpenAI Agents SDK (`openai-agents`), Official MCP SDK (`mcp`), SQLModel, asyncpg
- Frontend: Next.js 16+, OpenAI ChatKit (`@openai/chatkit`), Better Auth (existing from Phase II)

**Storage**: Neon Serverless PostgreSQL (existing from Phase II, adding Conversation and Message tables)
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web application (Linux server for backend, modern browsers for frontend)
**Project Type**: Web application (frontend + backend, extending existing Phase II structure)
**Performance Goals**:
- Message response time: <3 seconds for 95% of requests
- Task operation success rate: 99%+
- Support 100 concurrent users without degradation
- Natural language intent recognition: 85%+ accuracy

**Constraints**:
- Stateless server architecture (no in-memory session storage)
- All conversation state must persist to database
- Each request must be independently processable
- Horizontal scalability required
- Response times must support real-time chat experience
- Must integrate with existing Phase II authentication and task schema

**Scale/Scope**:
- 100 concurrent users
- Typical conversations: <100 messages
- Task titles: 1-200 characters
- Task descriptions: max 1000 characters
- 5 MCP tools to implement
- 1 chat API endpoint
- 2 new database tables (Conversation, Message)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Spec-Driven Development Compliance
- [x] Feature specification exists and is complete (`spec.md`)
- [x] All user stories have acceptance criteria
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- **Status**: PASS - Specification complete with 7 user stories, 20 functional requirements, 14 success criteria

### ✅ Technology Stack Adherence (Phase III)
- [x] Frontend: OpenAI ChatKit (mandated by constitution)
- [x] Backend: Python FastAPI (mandated by constitution)
- [x] AI Framework: OpenAI Agents SDK (mandated by constitution)
- [x] MCP Server: Official MCP SDK (mandated by constitution)
- [x] Database: Neon Serverless PostgreSQL (existing from Phase II)
- [x] Authentication: Better Auth (existing from Phase II)
- **Status**: PASS - All technologies align with constitution Phase III requirements

### ✅ Architecture Principles
- [x] Stateless server design (FR-020, explicitly required)
- [x] Database-backed state (Conversation and Message entities)
- [x] User isolation enforced (FR-014)
- [x] Clean separation: Frontend (ChatKit) → Backend (FastAPI) → MCP Server → Database
- **Status**: PASS - Architecture follows constitution principles

### ✅ Clean Code & Simplicity (YAGNI)
- [x] No premature optimization - building only required features
- [x] Smallest viable diff - extending existing Phase II structure
- [x] Single responsibility - MCP tools are focused, stateless functions
- [x] No hardcoded secrets - using environment variables for API keys
- **Status**: PASS - Design follows YAGNI and clean code principles

### ✅ Test-First Development
- [x] Acceptance criteria defined for all user stories
- [x] Edge cases identified in specification
- [x] Testing strategy: pytest for backend, Jest for frontend
- [x] Contract testing for MCP tools
- **Status**: PASS - Test requirements clear, TDD workflow can be followed

### ⚠️ Complexity Assessment
**No violations detected** - This is a straightforward extension of Phase II:
- Reusing existing authentication system
- Reusing existing task database schema
- Adding 2 new tables (Conversation, Message) - justified by conversation persistence requirement
- Adding 1 new endpoint (chat) - justified by conversational interface requirement
- Adding 5 MCP tools - mandated by constitution and specification

**Conclusion**: All constitution gates PASS. No complexity violations. Ready for Phase 0 research.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-ai-chatbot/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   ├── chat-api.yaml    # OpenAPI spec for chat endpoint
│   └── mcp-tools.yaml   # MCP tool definitions
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Web application structure (extending existing Phase II)
backend/
├── src/
│   ├── models/
│   │   ├── task.py              # Existing from Phase II
│   │   ├── user.py              # Existing from Phase II
│   │   ├── conversation.py      # NEW: Conversation model
│   │   └── message.py           # NEW: Message model
│   ├── services/
│   │   ├── task_service.py      # Existing from Phase II
│   │   └── conversation_service.py  # NEW: Conversation management
│   ├── api/
│   │   ├── tasks.py             # Existing from Phase II
│   │   └── chat.py              # NEW: Chat endpoint
│   ├── mcp/
│   │   ├── server.py            # NEW: MCP server setup
│   │   └── tools.py             # NEW: MCP tool implementations
│   └── agents/
│       ├── todo_agent.py        # NEW: Agent configuration
│       └── runner.py            # NEW: Agent execution logic
└── tests/
    ├── unit/
    │   ├── test_mcp_tools.py    # NEW: MCP tool tests
    │   └── test_agent.py        # NEW: Agent tests
    ├── integration/
    │   └── test_chat_endpoint.py  # NEW: Chat endpoint tests
    └── contract/
        └── test_mcp_contracts.py  # NEW: MCP contract tests

frontend/
├── src/
│   ├── components/
│   │   ├── TaskList.tsx         # Existing from Phase II
│   │   └── ChatInterface.tsx    # NEW: ChatKit integration
│   ├── pages/
│   │   ├── tasks.tsx            # Existing from Phase II
│   │   └── chat.tsx             # NEW: Chat page
│   └── services/
│       ├── taskService.ts       # Existing from Phase II
│       └── chatService.ts       # NEW: Chat API client
└── tests/
    ├── components/
    │   └── ChatInterface.test.tsx  # NEW: Chat component tests
    └── integration/
        └── chat.test.tsx          # NEW: Chat flow tests
```

**Structure Decision**: Extending existing Phase II web application structure. Backend adds new directories for MCP server (`mcp/`) and agent logic (`agents/`). Frontend adds chat interface component and page. This maintains separation of concerns while building on existing authentication and task management infrastructure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. This section is not applicable.

---

## Phase 0: Research & Technology Decisions

*Status: COMPLETE*

Since Phase III technologies are mandated by the constitution, research focuses on implementation patterns and best practices rather than technology selection.

### Research Tasks

1. **OpenAI Agents SDK Integration Patterns** ✅
   - Research: Agent initialization, instruction design, tool registration
   - Research: Runner execution (sync vs async), context variables
   - Research: Conversation history management
   - Output: Best practices for stateless agent design

2. **MCP Server Implementation** ✅
   - Research: MCP server setup with Official MCP SDK
   - Research: Tool definition patterns, schema validation
   - Research: Stateless tool design with database integration
   - Output: MCP tool implementation patterns

3. **ChatKit Frontend Integration** ✅
   - Research: ChatKit component setup and configuration
   - Research: Domain allowlist configuration for production
   - Research: Message state management and optimistic updates
   - Output: ChatKit integration best practices

4. **Stateless Architecture Patterns** ✅
   - Research: Database-backed conversation state
   - Research: Horizontal scaling considerations
   - Research: Session management without server-side state
   - Output: Stateless chat endpoint design pattern

5. **Natural Language Processing Patterns** ✅
   - Research: Intent recognition for task operations
   - Research: Entity extraction (task titles, IDs)
   - Research: Ambiguity handling and clarification strategies
   - Output: NLP patterns for task management

**Output**: [research.md](./research.md) - Complete research findings with implementation patterns

---

## Phase 1: Design & Contracts

*Status: COMPLETE*

### Data Model Design ✅

Generated [data-model.md](./data-model.md) with:
- Conversation entity (extends existing schema)
- Message entity (extends existing schema)
- Relationships to existing User and Task entities
- State transitions for conversation lifecycle
- SQL schemas and SQLModel definitions
- Migration strategy (Phase II → Phase III)

### API Contracts ✅

Generated contracts in [/contracts/](./contracts/):
- [chat-api.yaml](./contracts/chat-api.yaml): OpenAPI specification for POST /api/{user_id}/chat endpoint
  - Request/response schemas
  - Error handling (400, 401, 403, 404, 500, 503)
  - Additional endpoints for conversation management
- [mcp-tools.yaml](./contracts/mcp-tools.yaml): MCP tool definitions for 5 task operations
  - add_task, list_tasks, complete_task, delete_task, update_task
  - Input/output schemas with validation rules
  - Error codes and messages
  - Agent integration patterns

### Quick Start Guide ✅

Generated [quickstart.md](./quickstart.md) with:
- Development environment setup (Python 3.13+, Node.js 18+)
- Running MCP server locally (port 8001)
- Testing chat endpoint (curl examples)
- ChatKit configuration (domain allowlist)
- Troubleshooting guide
- Useful commands and resources

### Agent Context Update ✅

Updated Claude agent context file (CLAUDE.md) with Phase III technologies:
- Python 3.13+ (backend), TypeScript/Next.js 16+ (frontend)
- Neon Serverless PostgreSQL with new tables (Conversation, Message)

---

## Post-Design Constitution Check

*Re-evaluation after Phase 1 design completion*

### ✅ Spec-Driven Development Compliance
- [x] All design artifacts trace back to specification requirements
- [x] Data model entities map to spec entities (Conversation, Message)
- [x] API contracts implement functional requirements (FR-001 to FR-020)
- [x] Success criteria remain testable with current design
- **Status**: PASS - Design fully implements specification

### ✅ Technology Stack Adherence (Phase III)
- [x] OpenAI Agents SDK: Confirmed in research.md and quickstart.md
- [x] Official MCP SDK: Confirmed in mcp-tools.yaml and quickstart.md
- [x] OpenAI ChatKit: Confirmed in quickstart.md frontend setup
- [x] FastAPI: Confirmed in chat-api.yaml and quickstart.md
- [x] Neon PostgreSQL: Confirmed in data-model.md with new tables
- **Status**: PASS - All mandated technologies used correctly

### ✅ Architecture Principles
- [x] Stateless server: Confirmed in chat-api.yaml (loads history from DB per request)
- [x] Database-backed state: Confirmed in data-model.md (Conversation and Message tables)
- [x] User isolation: Confirmed in mcp-tools.yaml (all tools require user_id, validate ownership)
- [x] Clean separation: Frontend (ChatKit) → Backend (FastAPI) → MCP Server → Database
- [x] Horizontal scalability: Stateless design enables load balancing
- **Status**: PASS - Architecture follows all principles

### ✅ Clean Code & Simplicity (YAGNI)
- [x] Minimal schema changes: Only 2 new tables (Conversation, Message)
- [x] No premature optimization: Simple CRUD operations, no caching layer
- [x] Single responsibility: Each MCP tool does one thing (add, list, complete, delete, update)
- [x] No feature creep: Only implements specified requirements
- [x] Reuses Phase II: Authentication, User, Task entities unchanged
- **Status**: PASS - Design is minimal and focused

### ✅ Test-First Development
- [x] Acceptance criteria defined in spec.md for all user stories
- [x] Contract tests defined in mcp-tools.yaml (input/output schemas)
- [x] API contract tests defined in chat-api.yaml (request/response validation)
- [x] Testing strategy documented in quickstart.md (unit, integration, contract, e2e)
- [x] Error scenarios documented in contracts (validation, permission, not found)
- **Status**: PASS - Comprehensive testing strategy in place

### ✅ Security & Data Integrity
- [x] Authentication: JWT tokens from Better Auth (existing Phase II)
- [x] Authorization: User isolation enforced in all MCP tools
- [x] Input validation: Length limits, format checks in mcp-tools.yaml
- [x] SQL injection prevention: SQLModel ORM with parameterized queries
- [x] UUID primary keys: Per constitution v1.1.0 (data-model.md)
- [x] Cascade deletes: Proper foreign key constraints (data-model.md)
- **Status**: PASS - Security requirements met

### ⚠️ Complexity Assessment (Post-Design)
**Changes from initial assessment**:
- Added 2 database tables: Conversation (4 fields), Message (6 fields) - JUSTIFIED by conversation persistence requirement
- Added 1 REST endpoint: POST /api/{user_id}/chat - JUSTIFIED by conversational interface requirement
- Added 2 supporting endpoints: GET /api/{user_id}/conversations, GET /api/{user_id}/conversations/{id} - JUSTIFIED by conversation history requirement
- Added 5 MCP tools: add_task, list_tasks, complete_task, delete_task, update_task - MANDATED by constitution
- Added 3 new backend modules: mcp/server.py, mcp/tools.py, agents/todo_agent.py - JUSTIFIED by MCP and agent requirements
- Added 1 new frontend component: ChatInterface.tsx - JUSTIFIED by ChatKit integration requirement

**Complexity Justification**:
All additions are directly traceable to specification requirements and constitution mandates. No unnecessary abstractions or premature optimizations introduced. Design follows YAGNI principle.

**Conclusion**: No constitution violations. All complexity is justified and necessary.

### 📋 Architectural Decisions Requiring ADR

Based on the three-part test (Impact + Alternatives + Scope):

1. **Stateless Agent Architecture with Database-Backed Conversation History**
   - Impact: ✅ Long-term (affects scalability, deployment, state management)
   - Alternatives: ✅ Multiple options considered (in-memory, Redis, database)
   - Scope: ✅ Cross-cutting (affects backend, database, deployment)
   - **Recommendation**: Document with `/sp.adr stateless-agent-architecture`

2. **MCP Server as Separate Process vs Embedded Tools**
   - Impact: ✅ Long-term (affects deployment, testing, tool reusability)
   - Alternatives: ✅ Multiple options (separate server, embedded, hybrid)
   - Scope: ✅ Cross-cutting (affects backend architecture, deployment)
   - **Recommendation**: Document with `/sp.adr mcp-server-architecture`

3. **UUID Primary Keys for All Entities**
   - Impact: ✅ Long-term (affects data model, migrations, API contracts)
   - Alternatives: ✅ Multiple options (UUID, auto-increment, composite)
   - Scope: ✅ Cross-cutting (affects database, API, security)
   - **Note**: Already mandated by constitution v1.1.0, but rationale should be documented
   - **Recommendation**: Document with `/sp.adr uuid-primary-keys`

**Final Constitution Check**: ✅ PASS - All gates passed, design is ready for implementation

---

## Phase 2: Task Breakdown

*Status: NOT STARTED (separate /sp.tasks command)*

Task generation will be handled by `/sp.tasks` command after this plan is complete.

**Next Step**: Run `/sp.tasks` to generate actionable implementation tasks.

---

## Summary

**Planning Phase Complete** ✅

**Artifacts Generated**:
1. [research.md](./research.md) - Implementation patterns and best practices
2. [data-model.md](./data-model.md) - Database schema and entities
3. [contracts/chat-api.yaml](./contracts/chat-api.yaml) - REST API specification
4. [contracts/mcp-tools.yaml](./contracts/mcp-tools.yaml) - MCP tool definitions
5. [quickstart.md](./quickstart.md) - Developer setup guide

**Constitution Compliance**: All gates passed (pre-design and post-design)

**Recommended ADRs**: 3 architectural decisions identified for documentation

**Ready for**: Task generation (`/sp.tasks`) and implementation

---

## Notes

- This plan extends existing Phase II infrastructure (authentication, task schema, database)
- All new components follow stateless architecture principle
- MCP tools provide standardized interface between AI agent and task operations
- ChatKit provides production-ready chat UI component
- Conversation persistence enables resuming chats after server restart
- Design is minimal, focused, and fully traceable to specification requirements
