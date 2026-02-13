# Tasks: Phase II - Todo Full-Stack Web Application

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-15
**Status**: Ready for Implementation

## Task Format

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

- **TaskID**: Unique identifier (T001, T002, etc.)
- **P?**: Priority (P1=Critical, P2=Important, P3=Nice-to-have)
- **Story?**: User Story reference (US1-US5)
- **Description**: Clear, actionable task description
- **file path**: Specific file(s) to create or modify

---

## Phase 0: Setup & Infrastructure (Foundation)

### Backend Setup

- [ ] [T001] [P1] Create backend directory structure with app/ subdirectories (models, routes, services, config) - `backend/app/`
- [ ] [T002] [P1] Create requirements.txt with FastAPI, SQLModel, psycopg2-binary, python-jose, passlib, pytest dependencies - `backend/requirements.txt`
- [ ] [T003] [P1] Create .env.example with DATABASE_URL, BETTER_AUTH_SECRET, CORS_ORIGINS placeholders - `backend/.env.example`
- [ ] [T004] [P1] Create backend configuration module to load environment variables using pydantic-settings - `backend/app/config.py`
- [ ] [T005] [P1] Create database connection module with SQLModel engine and session management - `backend/app/database.py`
- [ ] [T006] [P1] Create main FastAPI application with CORS middleware configured - `backend/app/main.py`

### Frontend Setup

- [ ] [T007] [P1] Create frontend directory with Next.js 16+ App Router structure - `frontend/`
- [ ] [T008] [P1] Initialize package.json with Next.js, React, Better Auth, TypeScript, Tailwind CSS dependencies - `frontend/package.json`
- [ ] [T009] [P1] Create .env.local.example with NEXT_PUBLIC_API_URL and BETTER_AUTH_SECRET placeholders - `frontend/.env.local.example`
- [ ] [T010] [P1] Configure Tailwind CSS with tailwind.config.js and globals.css - `frontend/tailwind.config.js`, `frontend/app/globals.css`
- [ ] [T011] [P1] Create TypeScript configuration with path aliases (@/) - `frontend/tsconfig.json`
- [ ] [T012] [P1] Create API client utility for making authenticated requests to backend - `frontend/lib/api-client.ts`

### Database Models

- [ ] [T013] [P1] Create User SQLModel with id, email, hashed_password, created_at, updated_at fields - `backend/app/models/user.py`
- [ ] [T014] [P1] Create Task SQLModel with id, user_id, title, description, is_complete, created_at, updated_at fields - `backend/app/models/task.py`
- [ ] [T015] [P1] Create database initialization script to create tables using SQLModel.metadata.create_all() - `backend/app/database.py`
- [ ] [T016] [P1] Add indexes for users.email, tasks.user_id, tasks.created_at, tasks.user_created composite - `backend/app/models/`

---

## Phase 1: User Story 1 - User Registration and Authentication (P1)

### Backend Authentication

- [ ] [T017] [P1] [US1] Create password hashing utilities using passlib with bcrypt - `backend/app/services/auth.py`
- [ ] [T018] [P1] [US1] Create JWT token generation function with 7-day expiration - `backend/app/services/auth.py`
- [ ] [T019] [P1] [US1] Create JWT token validation function with signature and expiration checks - `backend/app/services/auth.py`
- [ ] [T020] [P1] [US1] Create authentication dependency to extract and validate JWT from Authorization header - `backend/app/dependencies/auth.py`
- [ ] [T021] [P1] [US1] Create POST /api/auth/signup endpoint with email validation and duplicate check - `backend/app/routes/auth.py`
- [ ] [T022] [P1] [US1] Create POST /api/auth/signin endpoint with credential verification - `backend/app/routes/auth.py`
- [ ] [T023] [P1] [US1] Create POST /api/auth/signout endpoint (informational, frontend removes token) - `backend/app/routes/auth.py`
- [ ] [T024] [P1] [US1] Add Pydantic schemas for SignupRequest, SigninRequest, AuthResponse - `backend/app/schemas/auth.py`

### Frontend Authentication

- [ ] [T025] [P1] [US1] Create Better Auth configuration with JWT secret and providers - `frontend/lib/auth.ts`
- [ ] [T026] [P1] [US1] Create authentication context provider for managing user state - `frontend/contexts/AuthContext.tsx`
- [ ] [T027] [P1] [US1] Create useAuth hook for accessing authentication state and methods - `frontend/hooks/useAuth.ts`
- [ ] [T028] [P1] [US1] Create signup page with email/password form at /signup - `frontend/app/signup/page.tsx`
- [ ] [T029] [P1] [US1] Create signin page with email/password form at /signin - `frontend/app/signin/page.tsx`
- [ ] [T030] [P1] [US1] Create SignupForm component with validation and error handling - `frontend/components/auth/SignupForm.tsx`
- [ ] [T031] [P1] [US1] Create SigninForm component with validation and error handling - `frontend/components/auth/SigninForm.tsx`
- [ ] [T032] [P1] [US1] Create protected route wrapper to redirect unauthenticated users to /signin - `frontend/components/auth/ProtectedRoute.tsx`
- [ ] [T033] [P1] [US1] Create landing page with navigation to signup/signin at / - `frontend/app/page.tsx`

### Authentication Tests

- [ ] [T034] [P1] [US1] Write backend test for successful user signup with valid credentials - `backend/tests/test_auth.py`
- [ ] [T035] [P1] [US1] Write backend test for duplicate email rejection during signup - `backend/tests/test_auth.py`
- [ ] [T036] [P1] [US1] Write backend test for successful signin with valid credentials - `backend/tests/test_auth.py`
- [ ] [T037] [P1] [US1] Write backend test for signin failure with invalid credentials - `backend/tests/test_auth.py`
- [ ] [T038] [P1] [US1] Write backend test for JWT token validation and expiration - `backend/tests/test_auth.py`
- [ ] [T039] [P1] [US1] Write frontend test for SignupForm component rendering and submission - `frontend/tests/components/SignupForm.test.tsx`
- [ ] [T040] [P1] [US1] Write frontend test for SigninForm component rendering and submission - `frontend/tests/components/SigninForm.test.tsx`

---

## Phase 2: User Story 2 - Create and View Personal Tasks (P1)

### Backend Task CRUD - Create & Read

- [ ] [T041] [P1] [US2] Create POST /api/{user_id}/tasks endpoint to create new task with ownership check - `backend/app/routes/tasks.py`
- [ ] [T042] [P1] [US2] Create GET /api/{user_id}/tasks endpoint to retrieve all user's tasks sorted by created_at DESC - `backend/app/routes/tasks.py`
- [ ] [T043] [P1] [US2] Create GET /api/{user_id}/tasks/{id} endpoint to retrieve single task with ownership check - `backend/app/routes/tasks.py`
- [ ] [T044] [P1] [US2] Add Pydantic schemas for CreateTaskRequest, TaskResponse, TaskListResponse - `backend/app/schemas/task.py`
- [ ] [T045] [P1] [US2] Create task service layer with create_task and get_user_tasks functions - `backend/app/services/task.py`
- [ ] [T046] [P1] [US2] Add validation for title (1-200 chars, not only whitespace) and description (max 1000 chars) - `backend/app/schemas/task.py`

### Frontend Task Management - Create & View

- [ ] [T047] [P1] [US2] Create task dashboard page at /dashboard with protected route - `frontend/app/dashboard/page.tsx`
- [ ] [T048] [P1] [US2] Create TaskList component to display array of tasks - `frontend/components/tasks/TaskList.tsx`
- [ ] [T049] [P1] [US2] Create TaskItem component to display individual task with title, description, status - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T050] [P1] [US2] Create CreateTaskForm component with title and description inputs - `frontend/components/tasks/CreateTaskForm.tsx`
- [ ] [T051] [P1] [US2] Create EmptyState component to display when user has no tasks - `frontend/components/tasks/EmptyState.tsx`
- [ ] [T052] [P1] [US2] Create useTasks hook for fetching and managing task state - `frontend/hooks/useTasks.ts`
- [ ] [T053] [P1] [US2] Implement task creation API call in dashboard with optimistic UI update - `frontend/app/dashboard/page.tsx`
- [ ] [T054] [P1] [US2] Implement task list fetching on dashboard mount with loading state - `frontend/app/dashboard/page.tsx`

### Task Create & View Tests

- [ ] [T055] [P1] [US2] Write backend test for creating task with valid title and description - `backend/tests/test_tasks.py`
- [ ] [T056] [P1] [US2] Write backend test for creating task with only title (no description) - `backend/tests/test_tasks.py`
- [ ] [T057] [P1] [US2] Write backend test for rejecting task with empty title - `backend/tests/test_tasks.py`
- [ ] [T058] [P1] [US2] Write backend test for rejecting task with title exceeding 200 characters - `backend/tests/test_tasks.py`
- [ ] [T059] [P1] [US2] Write backend test for retrieving all tasks for authenticated user - `backend/tests/test_tasks.py`
- [ ] [T060] [P1] [US2] Write backend test for data isolation (user cannot see other user's tasks) - `backend/tests/test_tasks.py`
- [ ] [T061] [P1] [US2] Write frontend test for TaskList component rendering multiple tasks - `frontend/tests/components/TaskList.test.tsx`
- [ ] [T062] [P1] [US2] Write frontend test for TaskItem component displaying task details - `frontend/tests/components/TaskItem.test.tsx`
- [ ] [T063] [P1] [US2] Write frontend test for CreateTaskForm submission and validation - `frontend/tests/components/CreateTaskForm.test.tsx`
- [ ] [T064] [P1] [US2] Write frontend test for EmptyState component display - `frontend/tests/components/EmptyState.test.tsx`

---

## Phase 3: User Story 3 - Mark Tasks as Complete or Incomplete (P2)

### Backend Task Completion

- [ ] [T065] [P2] [US3] Create PATCH /api/{user_id}/tasks/{id}/complete endpoint to toggle completion status - `backend/app/routes/tasks.py`
- [ ] [T066] [P2] [US3] Add Pydantic schema for ToggleCompleteRequest with is_complete boolean - `backend/app/schemas/task.py`
- [ ] [T067] [P2] [US3] Create toggle_task_completion service function with ownership check - `backend/app/services/task.py`
- [ ] [T068] [P2] [US3] Update Task model's updated_at timestamp when completion status changes - `backend/app/services/task.py`

### Frontend Task Completion

- [ ] [T069] [P2] [US3] Add completion toggle button/checkbox to TaskItem component - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T070] [P2] [US3] Add visual styling to distinguish completed tasks (strikethrough, opacity, color) - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T071] [P2] [US3] Implement toggle completion API call with optimistic UI update - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T072] [P2] [US3] Add loading state during completion toggle operation - `frontend/components/tasks/TaskItem.tsx`

### Task Completion Tests

- [ ] [T073] [P2] [US3] Write backend test for marking incomplete task as complete - `backend/tests/test_tasks.py`
- [ ] [T074] [P2] [US3] Write backend test for marking complete task as incomplete - `backend/tests/test_tasks.py`
- [ ] [T075] [P2] [US3] Write backend test for completion status persistence across requests - `backend/tests/test_tasks.py`
- [ ] [T076] [P2] [US3] Write backend test for ownership check on completion toggle - `backend/tests/test_tasks.py`
- [ ] [T077] [P2] [US3] Write frontend test for TaskItem completion toggle interaction - `frontend/tests/components/TaskItem.test.tsx`
- [ ] [T078] [P2] [US3] Write frontend test for visual distinction between complete/incomplete tasks - `frontend/tests/components/TaskItem.test.tsx`

---

## Phase 4: User Story 4 - Update Task Details (P3)

### Backend Task Update

- [ ] [T079] [P3] [US4] Create PUT /api/{user_id}/tasks/{id} endpoint to update task title and description - `backend/app/routes/tasks.py`
- [ ] [T080] [P3] [US4] Add Pydantic schema for UpdateTaskRequest with title and description fields - `backend/app/schemas/task.py`
- [ ] [T081] [P3] [US4] Create update_task service function with ownership check and validation - `backend/app/services/task.py`
- [ ] [T082] [P3] [US4] Update Task model's updated_at timestamp when task is modified - `backend/app/services/task.py`

### Frontend Task Update

- [ ] [T083] [P3] [US4] Create EditTaskForm component with title and description inputs - `frontend/components/tasks/EditTaskForm.tsx`
- [ ] [T084] [P3] [US4] Add edit mode toggle to TaskItem component (view/edit states) - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T085] [P3] [US4] Implement task update API call with optimistic UI update - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T086] [P3] [US4] Add cancel button to revert changes and exit edit mode - `frontend/components/tasks/EditTaskForm.tsx`
- [ ] [T087] [P3] [US4] Add validation to prevent saving task with empty title - `frontend/components/tasks/EditTaskForm.tsx`

### Task Update Tests

- [ ] [T088] [P3] [US4] Write backend test for updating task title only - `backend/tests/test_tasks.py`
- [ ] [T089] [P3] [US4] Write backend test for updating task description only - `backend/tests/test_tasks.py`
- [ ] [T090] [P3] [US4] Write backend test for updating both title and description - `backend/tests/test_tasks.py`
- [ ] [T091] [P3] [US4] Write backend test for rejecting update with empty title - `backend/tests/test_tasks.py`
- [ ] [T092] [P3] [US4] Write backend test for ownership check on task update - `backend/tests/test_tasks.py`
- [ ] [T093] [P3] [US4] Write frontend test for EditTaskForm rendering and submission - `frontend/tests/components/EditTaskForm.test.tsx`
- [ ] [T094] [P3] [US4] Write frontend test for edit mode toggle in TaskItem - `frontend/tests/components/TaskItem.test.tsx`
- [ ] [T095] [P3] [US4] Write frontend test for cancel button reverting changes - `frontend/tests/components/EditTaskForm.test.tsx`

---

## Phase 5: User Story 5 - Delete Tasks (P3)

### Backend Task Delete

- [ ] [T096] [P3] [US5] Create DELETE /api/{user_id}/tasks/{id} endpoint to permanently delete task - `backend/app/routes/tasks.py`
- [ ] [T097] [P3] [US5] Create delete_task service function with ownership check - `backend/app/services/task.py`
- [ ] [T098] [P3] [US5] Return 404 error if task not found or doesn't belong to user - `backend/app/routes/tasks.py`

### Frontend Task Delete

- [ ] [T099] [P3] [US5] Add delete button to TaskItem component - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T100] [P3] [US5] Create ConfirmDialog component for delete confirmation - `frontend/components/common/ConfirmDialog.tsx`
- [ ] [T101] [P3] [US5] Implement task deletion API call with optimistic UI update - `frontend/components/tasks/TaskItem.tsx`
- [ ] [T102] [P3] [US5] Show confirmation dialog before deleting task - `frontend/components/tasks/TaskItem.tsx`

### Task Delete Tests

- [ ] [T103] [P3] [US5] Write backend test for successful task deletion - `backend/tests/test_tasks.py`
- [ ] [T104] [P3] [US5] Write backend test for deletion persistence (task not retrievable after delete) - `backend/tests/test_tasks.py`
- [ ] [T105] [P3] [US5] Write backend test for ownership check on task deletion - `backend/tests/test_tasks.py`
- [ ] [T106] [P3] [US5] Write backend test for 404 error when deleting non-existent task - `backend/tests/test_tasks.py`
- [ ] [T107] [P3] [US5] Write frontend test for delete button click and confirmation dialog - `frontend/tests/components/TaskItem.test.tsx`
- [ ] [T108] [P3] [US5] Write frontend test for ConfirmDialog component behavior - `frontend/tests/components/ConfirmDialog.test.tsx`

---

## Phase 6: Polish & Integration

### Error Handling & Validation

- [ ] [T109] [P2] Create global error handler middleware in FastAPI for consistent error responses - `backend/app/middleware/error_handler.py`
- [ ] [T110] [P2] Create ErrorResponse schema with error, field, details properties - `backend/app/schemas/error.py`
- [ ] [T111] [P2] Add 401 Unauthorized response for missing/invalid JWT tokens - `backend/app/dependencies/auth.py`
- [ ] [T112] [P2] Add 403 Forbidden response for user_id mismatch in URL vs JWT - `backend/app/dependencies/auth.py`
- [ ] [T113] [P2] Create ErrorMessage component for displaying API errors in frontend - `frontend/components/common/ErrorMessage.tsx`
- [ ] [T114] [P2] Create LoadingSpinner component for async operation feedback - `frontend/components/common/LoadingSpinner.tsx`
- [ ] [T115] [P2] Add error boundary component to catch React errors - `frontend/components/common/ErrorBoundary.tsx`

### UI/UX Enhancements

- [ ] [T116] [P2] Create responsive navigation header with signout button - `frontend/components/layout/Header.tsx`
- [ ] [T117] [P2] Add loading states to all forms during submission - `frontend/components/`
- [ ] [T118] [P2] Add success toast notifications for task operations - `frontend/components/common/Toast.tsx`
- [ ] [T119] [P2] Ensure mobile responsiveness for all pages (320px minimum width) - `frontend/app/globals.css`
- [ ] [T120] [P2] Add focus states and keyboard navigation support for accessibility - `frontend/components/`

### Integration & Deployment

- [ ] [T121] [P1] Create backend Dockerfile for containerized deployment - `backend/Dockerfile`
- [ ] [T122] [P1] Create frontend deployment configuration for Vercel - `frontend/vercel.json`
- [ ] [T123] [P1] Write integration test for complete signup → create task → mark complete flow - `backend/tests/test_integration.py`
- [ ] [T124] [P1] Write integration test for data isolation between two users - `backend/tests/test_integration.py`
- [ ] [T125] [P1] Update README.md with setup instructions and architecture overview - `README.md`
- [ ] [T126] [P1] Create deployment guide with Neon, Vercel, and backend hosting instructions - `docs/DEPLOYMENT.md`

### Documentation & Final Checks

- [ ] [T127] [P2] Add API documentation using FastAPI's automatic OpenAPI generation - `backend/app/main.py`
- [ ] [T128] [P2] Add inline code comments for complex authentication and authorization logic - `backend/app/`
- [ ] [T129] [P2] Verify all 40 functional requirements (FR-001 to FR-040) are implemented - `specs/001-fullstack-web-app/spec.md`
- [ ] [T130] [P2] Verify all 16 success criteria (SC-001 to SC-016) are met - `specs/001-fullstack-web-app/spec.md`
- [ ] [T131] [P2] Run full test suite and ensure 100% pass rate - `backend/`, `frontend/`
- [ ] [T132] [P2] Perform manual testing of all user stories end-to-end - `specs/001-fullstack-web-app/spec.md`

---

## Task Summary

**Total Tasks**: 132
- **P1 (Critical)**: 64 tasks - Setup, Authentication, Create/View Tasks, Integration
- **P2 (Important)**: 30 tasks - Mark Complete, Error Handling, UI/UX, Documentation
- **P3 (Nice-to-have)**: 38 tasks - Update Tasks, Delete Tasks

**By User Story**:
- **Setup & Infrastructure**: 16 tasks
- **US1 - Authentication**: 23 tasks
- **US2 - Create/View Tasks**: 24 tasks
- **US3 - Mark Complete**: 14 tasks
- **US4 - Update Tasks**: 17 tasks
- **US5 - Delete Tasks**: 13 tasks
- **Polish & Integration**: 25 tasks

**By Type**:
- **Backend**: 52 tasks
- **Frontend**: 54 tasks
- **Tests**: 26 tasks

---

## Implementation Order

1. **Phase 0**: Complete all setup tasks (T001-T016) to establish foundation
2. **Phase 1**: Implement US1 Authentication (T017-T040) - enables user accounts
3. **Phase 2**: Implement US2 Create/View (T041-T064) - delivers core value
4. **Phase 3**: Implement US3 Mark Complete (T065-T078) - adds progress tracking
5. **Phase 4**: Implement US4 Update (T079-T095) - enables task refinement
6. **Phase 5**: Implement US5 Delete (T096-T108) - enables list cleanup
7. **Phase 6**: Polish & Integration (T109-T132) - production readiness

---

## Acceptance Criteria

Each task is considered complete when:
- [ ] Code is written and follows project conventions
- [ ] All related tests pass
- [ ] Code is committed to feature branch
- [ ] Task checkbox is marked complete in this file

Feature is ready for deployment when:
- [ ] All P1 tasks are complete
- [ ] All P2 tasks are complete
- [ ] All tests pass (backend pytest, frontend Jest)
- [ ] Manual testing confirms all user stories work end-to-end
- [ ] All 16 success criteria from spec.md are verified

---

**Last Updated**: 2026-01-15
**Next Step**: Begin implementation with Phase 0 setup tasks
