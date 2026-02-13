---
id: 004
title: TDD Compliance Test Tasks Addition
stage: misc
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: todo-ai-chatbot
branch: 001-todo-ai-chatbot
user: ALCL
command: Manual request (add test tasks to tasks.md)
labels: ["tdd", "testing", "constitution-compliance", "tasks", "red-green-refactor"]
links:
  spec: specs/001-todo-ai-chatbot/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-todo-ai-chatbot/tasks.md
tests:
  - TDD compliance validation - PASS (19 test tasks added)
  - Constitution alignment check - PASS (TDD violation resolved)
---

## Prompt

add test tasks to tasks.md

## Response snapshot

Added 19 test tasks to tasks.md to resolve CRITICAL TDD violation identified in `/sp.analyze`. The constitution mandates "Tests written BEFORE implementation" (Red-Green-Refactor cycle), but the original tasks.md contained zero test tasks.

**Test Tasks Added**:
- Phase 1 (Setup): +1 task (T006) - Test directory structure
- Phase 2 (Foundational): +4 tasks (T007-T008, T018, T022) - Model and endpoint unit/integration tests
- Phase 3 (US1 - Create Tasks): +2 tasks (T027-T028) - Contract + integration tests
- Phase 4 (US2 - View Tasks): +2 tasks (T035-T036) - Contract + integration tests
- Phase 5 (US3 - Complete Tasks): +2 tasks (T043-T044) - Contract + integration tests
- Phase 6 (US4 - Delete Tasks): +2 tasks (T051-T052) - Contract + integration tests
- Phase 7 (US5 - Update Tasks): +2 tasks (T059-T060) - Contract + integration tests
- Phase 8 (US7 - Resume Conversations): +1 task (T067) - Integration test
- Phase 9 (Frontend Integration): +2 tasks (T073-T074) - Component + integration tests
- Phase 10 (Polish): +1 task (T093) - Labeled test set for accuracy measurement

**Key Changes**:
- Total tasks increased from 75 to 94
- All test tasks marked with [TEST] indicator
- Test tasks positioned BEFORE implementation tasks (Red phase)
- Added pytest and jest to dependency installation tasks
- Created test directory structure task
- Documented Red-Green-Refactor workflow with examples
- Renumbered all tasks sequentially (T001-T094)
- Updated MVP scope to 48 tasks (includes test tasks)

**TDD Workflow Enforced**:
Each user story now follows:
1. RED Phase: Write tests (marked [TEST]) → Run → FAIL ❌
2. GREEN Phase: Implement feature → Run tests → PASS ✅
3. REFACTOR Phase: Improve code → Tests stay PASS ✅

**Test Coverage**:
- Unit tests: 3 (models, agent configuration)
- Contract tests: 10 (2 per user story for MCP tools)
- Integration tests: 6 (chat endpoint, user story flows, conversation persistence, frontend)

**Constitution Compliance**: ✅ RESOLVED
- Previous state: 0 test tasks (CRITICAL violation)
- Current state: 19 test tasks positioned before implementation
- TDD principle now enforced throughout task list

## Outcome

- ✅ Impact: Resolved CRITICAL TDD violation from constitution. Added 19 test tasks across all phases. Total tasks increased from 75 to 94. All implementation now follows Red-Green-Refactor cycle.
- 🧪 Tests: TDD compliance validation - PASS. Constitution alignment check - PASS. All test tasks properly positioned before implementation tasks.
- 📁 Files: Updated tasks.md (436 lines, was 368 lines). Added TDD compliance note, [TEST] markers, Red-Green-Refactor workflow documentation.
- 🔁 Next prompts: `/sp.implement` to execute all 94 tasks following TDD workflow
- 🧠 Reflection: Successfully resolved the CRITICAL constitution violation identified in `/sp.analyze`. The task list now properly enforces Test-First Development with clear Red-Green-Refactor cycles for each user story. Test tasks are marked with [TEST] indicator and positioned before implementation tasks. Added comprehensive test coverage including unit tests (models, agent), contract tests (MCP tools), and integration tests (endpoints, user flows, frontend). MVP scope updated to 48 tasks including tests. The implementation can now proceed with full TDD compliance.

## Evaluation notes (flywheel)

- Failure modes observed: None - test task addition completed successfully
- Graders run and results (PASS/FAIL): TDD compliance validation - PASS, Constitution alignment - PASS
- Prompt variant (if applicable): Manual fix request following `/sp.analyze` findings
- Next experiment (smallest change to try): Execute MVP tasks (Phases 1-4 + Phase 9) with TDD workflow to validate that Red-Green-Refactor cycle works as expected in practice
