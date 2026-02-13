# Tasks: Todo AI Chatbot

**Input**: Design documents from `/specs/001-todo-ai-chatbot/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

**TDD Compliance**: Test tasks are included BEFORE implementation tasks per constitution requirement.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- **[TEST]**: Test task that must FAIL before implementation (Red phase)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase-iii/backend/src/`
- **Frontend**: `phase-iii/frontend/src/`
- **Tests**: `phase-iii/backend/tests/` and `phase-iii/frontend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and dependency installation

- [X] T001 Install backend Phase III dependencies in phase-iii/backend/requirements.txt (openai-agents, mcp, asyncpg, pytest)
- [X] T002 [P] Install frontend Phase III dependencies in phase-iii/frontend/package.json (@openai/chatkit, jest, @testing-library/react)
- [X] T003 [P] Configure backend environment variables in phase-iii/backend/.env (OPENAI_API_KEY, MCP_SERVER_PORT)
- [X] T004 [P] Configure frontend environment variables in phase-iii/frontend/.env.local (NEXT_PUBLIC_OPENAI_DOMAIN_KEY)
- [X] T005 Create backend directory structure: phase-iii/backend/src/mcp/, phase-iii/backend/src/agents/, phase-iii/backend/src/models/conversation.py, phase-iii/backend/src/models/message.py
- [X] T006 [P] Create test directory structure: phase-iii/backend/tests/unit/, phase-iii/backend/tests/integration/, phase-iii/backend/tests/contract/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models & Migrations

- [X] T007 [TEST] Write unit test for Conversation model in phase-iii/backend/tests/unit/test_conversation_model.py (test field validation, relationships, timestamps)
- [X] T008 [P] [TEST] Write unit test for Message model in phase-iii/backend/tests/unit/test_message_model.py (test field validation, role enum, relationships)
- [X] T009 Create Conversation model in phase-iii/backend/src/models/conversation.py with SQLModel (id, user_id, created_at, updated_at)
- [X] T010 [P] Create Message model in phase-iii/backend/src/models/message.py with SQLModel (id, conversation_id, user_id, role, content, created_at)
- [X] T011 Update models __init__.py to export Conversation and Message models
- [X] T012 Create User model in phase-iii/backend/src/models/user.py with conversations relationship
- [ ] T013 Run database migrations to create Conversation and Message tables

### MCP Server Infrastructure

- [X] T014 Create MCP server initialization in phase-iii/backend/src/mcp/server.py with Official MCP SDK
- [X] T015 [P] Create MCP tools module structure in phase-iii/backend/src/mcp/tools.py with tool registration framework
- [X] T016 [P] Implement database session management for MCP tools in phase-iii/backend/src/mcp/database.py
- [X] T017 Add MCP server startup script in phase-iii/backend/src/mcp/__main__.py for running on port 8001

### Agent Configuration

- [X] T018 [TEST] Write unit test for agent configuration in phase-iii/backend/tests/unit/test_todo_agent.py (test agent initialization, instructions, model selection)
- [X] T019 Create agent configuration in phase-iii/backend/src/agents/todo_agent.py with OpenAI Agents SDK (Agent class, instructions, model selection)
- [X] T020 [P] Create agent runner module in phase-iii/backend/src/agents/runner.py with Runner.run_async() implementation
- [X] T021 [P] Implement conversation history loading in phase-iii/backend/src/services/conversation_service.py (load_conversation_history, store_message functions)

### Chat API Endpoint Infrastructure

- [X] T022 [TEST] Write integration test for chat endpoint in phase-iii/backend/tests/integration/test_chat_endpoint.py (test stateless request-response cycle)
- [X] T023 Create chat endpoint in phase-iii/backend/src/api/chat.py with POST /api/{user_id}/chat route
- [X] T024 [P] Implement conversation creation logic in phase-iii/backend/src/services/conversation_service.py (create_conversation, get_latest_conversation)
- [X] T025 [P] Add authentication middleware validation for chat endpoint in phase-iii/backend/src/api/chat.py
- [X] T026 Implement stateless request-response cycle in chat endpoint (load history → execute agent → store response)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Create Tasks Through Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can create new todo tasks by describing them in natural language

**Independent Test**: Send message "Add a task to buy groceries" and verify task is created with correct title

### Tests for User Story 1 (RED PHASE - Must FAIL before implementation)

- [X] T027 [P] [TEST] [US1] Write contract test for add_task MCP tool in phase-iii/backend/tests/contract/test_add_task_tool.py (test input schema, output schema, validation errors)
- [X] T028 [P] [TEST] [US1] Write integration test for task creation flow in phase-iii/backend/tests/integration/test_create_task_flow.py (test end-to-end: message → agent → tool → database)

### Implementation for User Story 1 (GREEN PHASE)

- [X] T029 [US1] Implement add_task MCP tool in phase-iii/backend/src/mcp/tools.py (input validation, database insert, return task_id)
- [X] T030 [US1] Register add_task tool with MCP server in phase-iii/backend/src/mcp/server.py
- [X] T031 [US1] Add agent instructions for task creation in phase-iii/backend/src/agents/todo_agent.py (trigger patterns: "add", "create", "remember")
- [X] T032 [US1] Implement task creation response formatting in agent instructions (confirmation message with task title)
- [X] T033 [US1] Add input validation for task titles (1-200 characters) in add_task tool
- [X] T034 [US1] Add error handling for invalid task creation requests in add_task tool

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks through natural language

---

## Phase 4: User Story 2 - View Tasks Through Conversation (Priority: P1) 🎯 MVP

**Goal**: Users can ask to see their tasks and receive a formatted list

**Independent Test**: Send message "Show me all my tasks" and verify accurate list is returned

### Tests for User Story 2 (RED PHASE - Must FAIL before implementation)

- [X] T035 [P] [TEST] [US2] Write contract test for list_tasks MCP tool in phase-iii/backend/tests/contract/test_list_tasks_tool.py (test input schema, output schema, status filtering)
- [X] T036 [P] [TEST] [US2] Write integration test for task listing flow in phase-iii/backend/tests/integration/test_list_tasks_flow.py (test end-to-end: message → agent → tool → response formatting)

### Implementation for User Story 2 (GREEN PHASE)

- [X] T037 [US2] Implement list_tasks MCP tool in phase-iii/backend/src/mcp/tools.py (query with user_id filter, status filtering, limit parameter)
- [X] T038 [US2] Register list_tasks tool with MCP server in phase-iii/backend/src/mcp/server.py
- [X] T039 [US2] Add agent instructions for task listing in phase-iii/backend/src/agents/todo_agent.py (trigger patterns: "show", "list", "what", "view")
- [X] T040 [US2] Implement task list formatting in agent instructions (numbered list with status indicators)
- [X] T041 [US2] Add status filtering logic in list_tasks tool (all, pending, completed)
- [X] T042 [US2] Add empty state handling in agent instructions (friendly message when no tasks exist)

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - MVP is complete

---

## Phase 5: User Story 3 - Complete Tasks Through Conversation (Priority: P2)

**Goal**: Users can mark tasks as complete by referencing them in natural language

**Independent Test**: Create a task, then send "Mark task 3 as complete" and verify status changes

### Tests for User Story 3 (RED PHASE - Must FAIL before implementation)

- [X] T043 [P] [TEST] [US3] Write contract test for complete_task MCP tool in phase-iii/backend/tests/contract/test_complete_task_tool.py (test input schema, output schema, ownership validation)
- [X] T044 [P] [TEST] [US3] Write integration test for task completion flow in phase-iii/backend/tests/integration/test_complete_task_flow.py (test task reference resolution by ID and description)

### Implementation for User Story 3 (GREEN PHASE)

- [X] T045 [US3] Implement complete_task MCP tool in phase-iii/backend/src/mcp/tools.py (task lookup, ownership validation, status update)
- [X] T046 [US3] Register complete_task tool with MCP server in phase-iii/backend/src/mcp/server.py
- [X] T047 [US3] Add agent instructions for task completion in phase-iii/backend/src/agents/todo_agent.py (trigger patterns: "done", "complete", "finished")
- [X] T048 [US3] Implement task reference resolution in agent instructions (by ID or by title search using case-insensitive substring match)
- [X] T049 [US3] Add error handling for non-existent tasks in complete_task tool
- [X] T050 [US3] Add confirmation message formatting in agent instructions (show completed task title)

**Checkpoint**: Task completion feature is now functional

---

## Phase 6: User Story 4 - Delete Tasks Through Conversation (Priority: P2)

**Goal**: Users can remove tasks they no longer need

**Independent Test**: Create a task, then send "Delete task 2" and verify task is removed

### Tests for User Story 4 (RED PHASE - Must FAIL before implementation)

- [X] T051 [P] [TEST] [US4] Write contract test for delete_task MCP tool in phase-iii/backend/tests/contract/test_delete_task_tool.py (test input schema, output schema, ownership validation)
- [X] T052 [P] [TEST] [US4] Write integration test for task deletion flow in phase-iii/backend/tests/integration/test_delete_task_flow.py (test ambiguity handling when multiple tasks match)

### Implementation for User Story 4 (GREEN PHASE)

- [X] T053 [US4] Implement delete_task MCP tool in phase-iii/backend/src/mcp/tools.py (task lookup, ownership validation, database delete)
- [X] T054 [US4] Register delete_task tool with MCP server in phase-iii/backend/src/mcp/server.py
- [X] T055 [US4] Add agent instructions for task deletion in phase-iii/backend/src/agents/todo_agent.py (trigger patterns: "delete", "remove", "cancel")
- [X] T056 [US4] Implement ambiguity handling in agent instructions (ask for clarification when multiple tasks match)
- [X] T057 [US4] Add error handling for non-existent tasks in delete_task tool
- [X] T058 [US4] Add confirmation message formatting in agent instructions (show deleted task title)

**Checkpoint**: Task deletion feature is now functional

---

## Phase 7: User Story 5 - Update Tasks Through Conversation (Priority: P3)

**Goal**: Users can modify existing task details through natural language

**Independent Test**: Create a task, then send "Change task 1 to 'Call mom tonight'" and verify title updates

### Tests for User Story 5 (RED PHASE - Must FAIL before implementation)

- [X] T059 [P] [TEST] [US5] Write contract test for update_task MCP tool in phase-iii/backend/tests/contract/test_update_task_tool.py (test input schema, output schema, partial updates)
- [X] T060 [P] [TEST] [US5] Write integration test for task update flow in phase-iii/backend/tests/integration/test_update_task_flow.py (test title-only, description-only, and combined updates)

### Implementation for User Story 5 (GREEN PHASE)

- [X] T061 [US5] Implement update_task MCP tool in phase-iii/backend/src/mcp/tools.py (task lookup, ownership validation, field updates)
- [X] T062 [US5] Register update_task tool with MCP server in phase-iii/backend/src/mcp/server.py
- [X] T063 [US5] Add agent instructions for task updates in phase-iii/backend/src/agents/todo_agent.py (trigger patterns: "change", "update", "rename")
- [X] T064 [US5] Implement partial update logic in update_task tool (title only, description only, or both)
- [X] T065 [US5] Add validation for updated fields in update_task tool (title 1-200 chars, description max 1000 chars)
- [X] T066 [US5] Add confirmation message formatting in agent instructions (show updated task details)

**Checkpoint**: All task management features are now complete

---

## Phase 8: User Story 7 - Resume Conversations After Interruption (Priority: P3)

**Goal**: Users can close the chat and return later to find conversation history preserved

**Independent Test**: Have a conversation, close browser, reopen, and verify history is visible

### Tests for User Story 7 (RED PHASE - Must FAIL before implementation)

- [X] T067 [P] [TEST] [US7] Write integration test for conversation persistence in phase-iii/backend/tests/integration/test_conversation_persistence.py (test conversation list, history retrieval, pruning)

### Implementation for User Story 7 (GREEN PHASE)

- [X] T068 [US7] Implement GET /api/{user_id}/conversations endpoint in phase-iii/backend/src/api/chat.py (list user's conversations)
- [X] T069 [US7] Implement GET /api/{user_id}/conversations/{id} endpoint in phase-iii/backend/src/api/chat.py (get conversation history)
- [ ] T070 [US7] Add conversation loading on chat interface mount in frontend (fetch latest conversation)
- [ ] T071 [US7] Implement conversation history display in frontend (show previous messages)
- [X] T072 [US7] Add conversation pruning logic in phase-iii/backend/src/services/conversation_service.py (limit to last 50 messages)

**Checkpoint**: Conversation persistence is now functional

---

## Phase 9: Frontend Integration

**Purpose**: Integrate ChatKit component and create chat interface

### Tests for Frontend Integration (RED PHASE - Must FAIL before implementation)

- [X] T073 [P] [TEST] Write component test for ChatInterface in phase-iii/frontend/tests/components/ChatInterface.test.tsx (test message sending, optimistic updates, error handling)
- [X] T074 [P] [TEST] Write integration test for chat flow in phase-iii/frontend/tests/integration/chat.test.tsx (test full user journey: login → chat → create task → view tasks)

### Implementation for Frontend Integration (GREEN PHASE)

- [X] T075 Create ChatInterface component in phase-iii/frontend/src/components/ChatInterface.tsx with ChatKit integration
- [X] T076 [P] Create chat page in phase-iii/frontend/src/pages/chat.tsx with authentication check
- [X] T077 [P] Implement message sending logic in ChatInterface component (POST to /api/{user_id}/chat)
- [X] T078 Implement optimistic updates in ChatInterface component (add user message immediately, rollback on error)
- [X] T079 [P] Add loading states and typing indicators in ChatInterface component
- [X] T080 [P] Implement error handling and user-friendly error messages in ChatInterface component (including AI service unavailability)
- [X] T081 Add conversation ID state management in ChatInterface component (store and pass conversation_id)
- [X] T082 [P] Style ChatInterface component to match application design system
- [X] T083 Add navigation link to chat page in phase-iii/frontend/src/components/Navigation.tsx

**Checkpoint**: Frontend chat interface is now fully functional

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T084 [P] Add comprehensive error handling across all MCP tools in phase-iii/backend/src/mcp/tools.py
- [ ] T085 [P] Add logging for all agent operations in phase-iii/backend/src/agents/runner.py
- [ ] T086 [P] Implement rate limiting for chat endpoint in phase-iii/backend/src/api/chat.py
- [ ] T087 [P] Add input sanitization for all user inputs in chat endpoint
- [X] T088 [P] Create API documentation in phase-iii/backend/docs/api.md
- [X] T089 [P] Update README.md with Phase III setup instructions
- [ ] T090 Run quickstart.md validation (verify all setup steps work)
- [ ] T091 [P] Add monitoring and metrics collection for chat endpoint
- [ ] T092 [P] Implement conversation history pruning for very long conversations (>100 messages)
- [ ] T093 [P] Create labeled test set (100 messages) for accuracy measurement per SC-002, SC-004, SC-011
- [ ] T094 Performance testing for 100 concurrent users

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
  - **TDD Flow**: Write tests (T007-T008, T018, T022) → Run tests (FAIL/RED) → Implement (T009-T026) → Run tests (PASS/GREEN)
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - **TDD Flow for each story**: Write tests → Run tests (FAIL/RED) → Implement → Run tests (PASS/GREEN)
  - US1 (Phase 3): Tests T027-T028 → Implementation T029-T034
  - US2 (Phase 4): Tests T035-T036 → Implementation T037-T042
  - US3 (Phase 5): Tests T043-T044 → Implementation T045-T050
  - US4 (Phase 6): Tests T051-T052 → Implementation T053-T058
  - US5 (Phase 7): Tests T059-T060 → Implementation T061-T066
  - US7 (Phase 8): Test T067 → Implementation T068-T072
- **Frontend Integration (Phase 9)**: Depends on at least US1 and US2 being complete (MVP)
  - **TDD Flow**: Tests T073-T074 → Implementation T075-T083
- **Polish (Phase 10)**: Depends on all desired user stories being complete

### TDD Workflow (Red-Green-Refactor)

**For each user story:**
1. **RED**: Write test tasks first (marked [TEST]) - tests MUST FAIL
2. **GREEN**: Implement feature tasks - tests MUST PASS
3. **REFACTOR**: Polish tasks improve code quality while keeping tests green

**Example for User Story 1:**
```bash
# RED Phase
1. Write T027: Contract test for add_task tool → Run → FAIL ❌
2. Write T028: Integration test for task creation → Run → FAIL ❌

# GREEN Phase
3. Implement T029-T034: add_task tool and agent instructions
4. Run T027 → PASS ✅
5. Run T028 → PASS ✅

# REFACTOR Phase (optional)
6. Improve code quality, add error handling
7. Re-run tests → Still PASS ✅
```

### Within Each User Story

- **Tests BEFORE implementation** (constitution requirement)
- Contract tests can run in parallel with integration tests
- Implementation tasks depend on tests being written (but not passing)
- Tests must FAIL before implementation begins
- Tests must PASS after implementation completes

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All test tasks marked [P] within a phase can be written in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user story TEST tasks can be written in parallel
- After tests are written, implementation for different user stories can proceed in parallel
- Frontend integration tasks marked [P] can run in parallel
- All Polish tasks marked [P] can run in parallel

---

## Parallel Example: User Story Tests (After Foundational Complete)

```bash
# Write all contract tests in parallel (RED phase):
Task: "Write contract test for add_task MCP tool" (T027)
Task: "Write contract test for list_tasks MCP tool" (T035)
Task: "Write contract test for complete_task MCP tool" (T043)
Task: "Write contract test for delete_task MCP tool" (T051)
Task: "Write contract test for update_task MCP tool" (T059)

# All tests should FAIL at this point ❌

# Then implement tools in parallel (GREEN phase):
Task: "Implement add_task MCP tool" (T029)
Task: "Implement list_tasks MCP tool" (T037)
Task: "Implement complete_task MCP tool" (T045)
Task: "Implement delete_task MCP tool" (T053)
Task: "Implement update_task MCP tool" (T061)

# All tests should PASS at this point ✅
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only) - TDD Approach

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational with TDD (T007-T026)
   - Write tests T007-T008, T018, T022 → FAIL ❌
   - Implement T009-T026 → Tests PASS ✅
3. Complete Phase 3: User Story 1 with TDD (T027-T034)
   - Write tests T027-T028 → FAIL ❌
   - Implement T029-T034 → Tests PASS ✅
4. Complete Phase 4: User Story 2 with TDD (T035-T042)
   - Write tests T035-T036 → FAIL ❌
   - Implement T037-T042 → Tests PASS ✅
5. Complete Phase 9: Frontend Integration with TDD (T073-T083)
   - Write tests T073-T074 → FAIL ❌
   - Implement T075-T083 → Tests PASS ✅
6. **STOP and VALIDATE**: All tests passing, MVP functional
7. Deploy/demo if ready

**MVP Delivers**: Users can create and view tasks through natural language conversation (with full test coverage)

### Incremental Delivery with TDD

1. Complete Setup + Foundational (with tests) → Foundation ready, all tests passing
2. Add User Story 1 (with tests) → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 (with tests) → Test independently → Deploy/Demo
4. Add User Story 3 (with tests) → Test independently → Deploy/Demo
5. Add User Story 4 (with tests) → Test independently → Deploy/Demo
6. Add User Story 5 (with tests) → Test independently → Deploy/Demo
7. Add User Story 7 (with tests) → Test independently → Deploy/Demo
8. Each story adds value without breaking previous stories (verified by tests)

---

## Task Summary

**Total Tasks**: 94 (was 75, added 19 test tasks)
- Phase 1 (Setup): 6 tasks (added test directory setup)
- Phase 2 (Foundational): 20 tasks (added 4 test tasks)
- Phase 3 (US1 - Create Tasks): 8 tasks (added 2 test tasks)
- Phase 4 (US2 - View Tasks): 8 tasks (added 2 test tasks)
- Phase 5 (US3 - Complete Tasks): 8 tasks (added 2 test tasks)
- Phase 6 (US4 - Delete Tasks): 8 tasks (added 2 test tasks)
- Phase 7 (US5 - Update Tasks): 8 tasks (added 2 test tasks)
- Phase 8 (US7 - Resume Conversations): 6 tasks (added 1 test task)
- Phase 9 (Frontend Integration): 11 tasks (added 2 test tasks)
- Phase 10 (Polish): 11 tasks (added 1 test task for accuracy measurement)

**Test Tasks**: 19 total
- Unit tests: 3 (models, agent)
- Contract tests: 10 (2 per user story for MCP tools)
- Integration tests: 6 (chat endpoint, user story flows, conversation persistence, frontend)

**Parallel Opportunities**: 45 tasks marked [P] can run in parallel within their phases

**MVP Scope**: Phases 1-4 + Phase 9 (48 tasks including tests) delivers core value with full test coverage

**TDD Compliance**: ✅ All implementation tasks now have corresponding test tasks that must be written and FAIL before implementation begins

**Independent Test Criteria** (now with automated tests):
- US1: Automated tests T027-T028 verify task creation
- US2: Automated tests T035-T036 verify task listing
- US3: Automated tests T043-T044 verify task completion
- US4: Automated tests T051-T052 verify task deletion
- US5: Automated tests T059-T060 verify task updates
- US7: Automated test T067 verifies conversation persistence
- Frontend: Automated tests T073-T074 verify chat interface

---

## Notes

- **[TEST]** marker indicates test tasks that must FAIL before implementation (Red phase)
- [P] tasks = different files, no dependencies within phase
- [Story] label maps task to specific user story for traceability
- Each user story follows Red-Green-Refactor cycle
- Tests must be written BEFORE implementation per constitution
- Commit after each Red-Green cycle (tests + implementation together)
- Stop at any checkpoint to validate story independently with automated tests
- User Story 6 (Maintain Conversation Context) is architectural - built into foundational phase
- All MCP tools follow stateless design pattern
- All endpoints enforce user isolation and authentication
- Database migrations must be run before any user story implementation
- Test coverage enables confident refactoring and prevents regressions
