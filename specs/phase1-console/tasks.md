# Tasks: Phase 1 - Todo Console Application

**Input**: Design documents from `/specs/phase1-console/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-interface.md

**Tests**: Included (TDD approach per Constitution - Test-First Development)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1-US5)
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and Python package structure

- [ ] T001 Create project directory structure per plan.md (`src/todo/`, `tests/`)
- [ ] T002 Initialize Python project with pyproject.toml for UV package manager
- [ ] T003 [P] Create `src/todo/__init__.py` with package version
- [ ] T004 [P] Configure pytest in pyproject.toml with testpaths and pythonpath
- [ ] T005 [P] Create `.gitignore` for Python project (venv, __pycache__, .pytest_cache)

**Checkpoint**: Project skeleton ready, `uv pip install -e .` should work

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 Create custom exceptions hierarchy in `src/todo/exceptions.py` (TodoError, ValidationError, EmptyTitleError, TitleTooLongError, DescriptionTooLongError, TaskNotFoundError)
- [ ] T007 [P] Create Task dataclass in `src/todo/models.py` with id, title, description, completed, created_at fields
- [ ] T008 [P] Add `to_dict()` method to Task model in `src/todo/models.py`
- [ ] T009 Create TaskManager class skeleton in `src/todo/manager.py` with `__init__`, `_tasks` dict, `_next_id` counter
- [ ] T010 [P] Implement validation functions `validate_title()` and `validate_description()` in `src/todo/manager.py`
- [ ] T011 [P] Create `tests/conftest.py` with pytest fixtures (task_manager, sample_task)
- [ ] T012 [P] Write unit tests for Task model in `tests/test_models.py` (creation, defaults, to_dict)
- [ ] T013 [P] Write unit tests for exceptions in `tests/test_models.py` (instantiation, messages)

**Checkpoint**: Foundation ready - `pytest tests/test_models.py` should pass

---

## Phase 3: User Story 1 - Add a New Task (Priority: P1) 🎯 MVP

**Goal**: Users can create new tasks with title and optional description

**Independent Test**: Run `add "Buy groceries"` and verify confirmation message with unique ID

### Tests for User Story 1

> **TDD: Write tests FIRST, ensure they FAIL before implementation**

- [ ] T014 [P] [US1] Write test `test_add_task_with_title_only` in `tests/test_manager.py`
- [ ] T015 [P] [US1] Write test `test_add_task_with_description` in `tests/test_manager.py`
- [ ] T016 [P] [US1] Write test `test_add_task_empty_title_raises_error` in `tests/test_manager.py`
- [ ] T017 [P] [US1] Write test `test_add_task_title_too_long_raises_error` in `tests/test_manager.py`
- [ ] T018 [P] [US1] Write test `test_add_task_generates_unique_sequential_ids` in `tests/test_manager.py`

### Implementation for User Story 1

- [ ] T019 [US1] Implement `add_task(title, description)` method in `src/todo/manager.py`
- [ ] T020 [US1] Implement `_generate_id()` private method in `src/todo/manager.py`
- [ ] T021 [US1] Run tests and verify all US1 tests pass

**Checkpoint**: `pytest tests/test_manager.py -k "add_task"` should pass

---

## Phase 4: User Story 2 - View All Tasks (Priority: P1)

**Goal**: Users can view all tasks with ID, title, description, and completion status

**Independent Test**: Add tasks, run `list`, verify all tasks displayed with status indicators

### Tests for User Story 2

- [ ] T022 [P] [US2] Write test `test_get_all_tasks_returns_list` in `tests/test_manager.py`
- [ ] T023 [P] [US2] Write test `test_get_all_tasks_empty_list` in `tests/test_manager.py`
- [ ] T024 [P] [US2] Write test `test_get_pending_tasks` in `tests/test_manager.py`
- [ ] T025 [P] [US2] Write test `test_get_completed_tasks` in `tests/test_manager.py`
- [ ] T026 [P] [US2] Write test `test_task_count` in `tests/test_manager.py`

### Implementation for User Story 2

- [ ] T027 [US2] Implement `get_task(task_id)` method in `src/todo/manager.py`
- [ ] T028 [US2] Implement `get_all_tasks()` method in `src/todo/manager.py`
- [ ] T029 [US2] Implement `get_pending_tasks()` method in `src/todo/manager.py`
- [ ] T030 [US2] Implement `get_completed_tasks()` method in `src/todo/manager.py`
- [ ] T031 [US2] Implement `task_count()` method in `src/todo/manager.py`
- [ ] T032 [US2] Run tests and verify all US2 tests pass

**Checkpoint**: `pytest tests/test_manager.py -k "get_"` should pass

---

## Phase 5: User Story 3 - Mark Task as Complete (Priority: P2)

**Goal**: Users can toggle task completion status

**Independent Test**: Add task, run `complete 1`, verify status changes to completed, run again to toggle back

### Tests for User Story 3

- [ ] T033 [P] [US3] Write test `test_toggle_complete_pending_to_completed` in `tests/test_manager.py`
- [ ] T034 [P] [US3] Write test `test_toggle_complete_completed_to_pending` in `tests/test_manager.py`
- [ ] T035 [P] [US3] Write test `test_toggle_complete_task_not_found` in `tests/test_manager.py`

### Implementation for User Story 3

- [ ] T036 [US3] Implement `toggle_complete(task_id)` method in `src/todo/manager.py`
- [ ] T037 [US3] Run tests and verify all US3 tests pass

**Checkpoint**: `pytest tests/test_manager.py -k "toggle"` should pass

---

## Phase 6: User Story 4 - Update Task Details (Priority: P3)

**Goal**: Users can update task title and/or description

**Independent Test**: Add task, run `update 1 --title "New title"`, verify title changed

### Tests for User Story 4

- [ ] T038 [P] [US4] Write test `test_update_task_title` in `tests/test_manager.py`
- [ ] T039 [P] [US4] Write test `test_update_task_description` in `tests/test_manager.py`
- [ ] T040 [P] [US4] Write test `test_update_task_both_fields` in `tests/test_manager.py`
- [ ] T041 [P] [US4] Write test `test_update_task_not_found` in `tests/test_manager.py`
- [ ] T042 [P] [US4] Write test `test_update_task_empty_title_raises_error` in `tests/test_manager.py`

### Implementation for User Story 4

- [ ] T043 [US4] Implement `update_task(task_id, title, description)` method in `src/todo/manager.py`
- [ ] T044 [US4] Run tests and verify all US4 tests pass

**Checkpoint**: `pytest tests/test_manager.py -k "update"` should pass

---

## Phase 7: User Story 5 - Delete a Task (Priority: P3)

**Goal**: Users can remove tasks from the list

**Independent Test**: Add task, run `delete 1`, verify task no longer appears in list

### Tests for User Story 5

- [ ] T045 [P] [US5] Write test `test_delete_task_success` in `tests/test_manager.py`
- [ ] T046 [P] [US5] Write test `test_delete_task_not_found` in `tests/test_manager.py`
- [ ] T047 [P] [US5] Write test `test_delete_task_id_not_reused` in `tests/test_manager.py`

### Implementation for User Story 5

- [ ] T048 [US5] Implement `delete_task(task_id)` method in `src/todo/manager.py`
- [ ] T049 [US5] Run tests and verify all US5 tests pass

**Checkpoint**: `pytest tests/test_manager.py -k "delete"` should pass. ALL TaskManager tests should now pass.

---

## Phase 8: CLI Interface

**Purpose**: Command-line interface connecting user input to TaskManager

### CLI Tests

- [ ] T050 [P] Write test `test_cli_add_command` in `tests/test_cli.py`
- [ ] T051 [P] Write test `test_cli_list_command` in `tests/test_cli.py`
- [ ] T052 [P] Write test `test_cli_complete_command` in `tests/test_cli.py`
- [ ] T053 [P] Write test `test_cli_update_command` in `tests/test_cli.py`
- [ ] T054 [P] Write test `test_cli_delete_command` in `tests/test_cli.py`
- [ ] T055 [P] Write test `test_cli_help_command` in `tests/test_cli.py`
- [ ] T056 [P] Write test `test_cli_unknown_command` in `tests/test_cli.py`

### CLI Implementation

- [ ] T057 Create argument parser with subcommands in `src/todo/cli.py`
- [ ] T058 Implement `handle_add()` command handler in `src/todo/cli.py`
- [ ] T059 Implement `handle_list()` command handler with --all/--pending/--completed flags in `src/todo/cli.py`
- [ ] T060 Implement `handle_complete()` command handler in `src/todo/cli.py`
- [ ] T061 Implement `handle_update()` command handler in `src/todo/cli.py`
- [ ] T062 Implement `handle_delete()` command handler in `src/todo/cli.py`
- [ ] T063 Implement `format_task_list()` output formatter in `src/todo/cli.py`
- [ ] T064 Implement `format_success()` and `format_error()` helpers in `src/todo/cli.py`

### Entry Point

- [ ] T065 Create `src/todo/__main__.py` with main() function
- [ ] T066 Implement interactive REPL mode in `src/todo/__main__.py`
- [ ] T067 Implement single-command mode in `src/todo/__main__.py`
- [ ] T068 Add graceful exit handling (Ctrl+C, Ctrl+D) in `src/todo/__main__.py`

**Checkpoint**: `python -m todo help` should display usage information

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, validation, and final touches

- [ ] T069 Create `README.md` with setup instructions, usage examples, and project overview
- [ ] T070 Update `CLAUDE.md` with Phase 1 specific context and file paths
- [ ] T071 [P] Run full test suite and verify ≥80% coverage (`pytest --cov=src/todo`)
- [ ] T072 [P] Run ruff linter and fix any PEP 8 violations
- [ ] T073 Verify all acceptance scenarios from spec.md pass manually
- [ ] T074 Test edge cases: empty title, long title (>200 chars), special characters, invalid task ID
- [ ] T075 Test both interactive REPL mode and single-command mode
- [ ] T076 Record demo video (max 90 seconds) demonstrating all 5 features

**Checkpoint**: All Definition of Done criteria met

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup ─────────────────────────────────────────────────┐
                                                                 │
Phase 2: Foundational ◄─────────────────────────────────────────┘
    │
    ├──► Phase 3: US1 - Add Task (P1) ────► MVP READY
    │
    ├──► Phase 4: US2 - View Tasks (P1) ──► Can start after Phase 2
    │
    ├──► Phase 5: US3 - Complete (P2) ────► Can start after Phase 2
    │
    ├──► Phase 6: US4 - Update (P3) ──────► Can start after Phase 2
    │
    └──► Phase 7: US5 - Delete (P3) ──────► Can start after Phase 2
                                                │
Phase 8: CLI Interface ◄────────────────────────┘ (needs all manager methods)
    │
Phase 9: Polish ◄───────────────────────────────┘
```

### User Story Independence

| Story | Dependencies | Can Start After |
|-------|--------------|-----------------|
| US1 (Add) | Foundational | Phase 2 |
| US2 (View) | Foundational | Phase 2 |
| US3 (Complete) | Foundational | Phase 2 |
| US4 (Update) | Foundational | Phase 2 |
| US5 (Delete) | Foundational | Phase 2 |

**Note**: US1 and US2 are both P1 priority. US2 (View) logically depends on US1 (Add) for meaningful testing, but the code itself is independent.

### Within Each User Story

1. Tests MUST be written FIRST and FAIL
2. Implementation follows
3. Tests MUST pass before moving to next story

---

## Parallel Execution Examples

### Phase 2: Foundational (Parallel Tasks)

```bash
# Can run in parallel (different files):
T007: Create Task dataclass in src/todo/models.py
T011: Create tests/conftest.py with fixtures
T012: Write unit tests for Task in tests/test_models.py
T013: Write unit tests for exceptions in tests/test_models.py
```

### User Story 1: Add Task (Parallel Tests)

```bash
# All US1 tests can run in parallel:
T014: test_add_task_with_title_only
T015: test_add_task_with_description
T016: test_add_task_empty_title_raises_error
T017: test_add_task_title_too_long_raises_error
T018: test_add_task_generates_unique_sequential_ids
```

### CLI Tests (Parallel)

```bash
# All CLI tests can run in parallel:
T050-T056: All test_cli_* tests
```

---

## Implementation Strategy

### MVP First (Recommended)

1. ✅ Complete Phase 1: Setup
2. ✅ Complete Phase 2: Foundational
3. ✅ Complete Phase 3: US1 (Add Task)
4. ✅ Complete Phase 4: US2 (View Tasks)
5. **STOP and VALIDATE**: Can add and view tasks
6. Continue with US3-US5, then CLI

### Suggested MVP Scope

**Minimum Viable Product = Setup + Foundational + US1 + US2**

This delivers:
- Ability to add tasks
- Ability to view tasks
- Core value proposition working

---

## Task Summary

| Phase | Tasks | Parallel Tasks |
|-------|-------|----------------|
| Setup | 5 | 3 |
| Foundational | 8 | 6 |
| US1: Add Task | 8 | 5 |
| US2: View Tasks | 11 | 5 |
| US3: Complete | 5 | 3 |
| US4: Update | 7 | 5 |
| US5: Delete | 5 | 3 |
| CLI Interface | 19 | 7 |
| Polish | 8 | 2 |
| **TOTAL** | **76** | **39** |

---

## Notes

- All test tasks marked [P] can run in parallel within their phase
- Commit after each completed task or logical group
- Run `pytest` after each implementation task to verify
- Stop at any checkpoint to validate independently
- Each user story should work on its own after completion
