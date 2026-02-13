# System Architecture: Phase II - Todo Full-Stack Web Application

**Feature Branch**: `001-fullstack-web-app`
**Created**: 2026-01-14
**Status**: Active Development

## High-Level Architecture

### Three-Tier Architecture

The application follows a standard three-tier web architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                         │
│                   (Next.js Frontend)                         │
│                                                              │
│  • User Interface Components                                │
│  • Client-Side Routing                                      │
│  • Form Validation                                          │
│  • JWT Token Storage                                        │
│  • API Client                                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTPS REST API
                            │ Authorization: Bearer <JWT>
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     APPLICATION TIER                         │
│                    (FastAPI Backend)                         │
│                                                              │
│  • RESTful API Endpoints                                    │
│  • JWT Verification Middleware                              │
│  • Business Logic                                           │
│  • Request Validation                                       │
│  • Authorization Checks                                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQL Queries (SQLModel ORM)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA TIER                              │
│                (Neon PostgreSQL Database)                    │
│                                                              │
│  • User Data Storage                                        │
│  • Task Data Storage                                        │
│  • Relational Integrity                                     │
│  • ACID Transactions                                        │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Architecture (Next.js 16+)

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication route group
│   │   ├── signup/
│   │   │   └── page.tsx          # Signup page
│   │   └── signin/
│   │       └── page.tsx          # Signin page
│   ├── (dashboard)/              # Protected route group
│   │   └── tasks/
│   │       └── page.tsx          # Task dashboard
│   ├── layout.tsx                # Root layout
│   └── page.tsx                  # Landing page
├── components/                   # Reusable UI components
│   ├── auth/
│   │   ├── SignupForm.tsx
│   │   └── SigninForm.tsx
│   ├── tasks/
│   │   ├── TaskList.tsx
│   │   ├── TaskItem.tsx
│   │   ├── TaskForm.tsx
│   │   └── TaskEditForm.tsx
│   └── ui/
│       ├── Button.tsx
│       ├── Input.tsx
│       └── LoadingSpinner.tsx
├── lib/                          # Utility libraries
│   ├── api-client.ts             # API communication
│   ├── auth.ts                   # Better Auth configuration
│   └── types.ts                  # TypeScript types
└── middleware.ts                 # Route protection middleware
```

**Key Responsibilities**:
- Render user interface
- Handle user interactions
- Validate form inputs (client-side)
- Store JWT token securely
- Make authenticated API requests
- Display loading states and errors
- Provide responsive design

### Backend Architecture (FastAPI)

```
backend/
├── app/
│   ├── main.py                   # FastAPI application entry
│   ├── config.py                 # Configuration management
│   ├── database.py               # Database connection
│   ├── models/                   # SQLModel data models
│   │   ├── user.py               # User model
│   │   └── task.py               # Task model
│   ├── schemas/                  # Pydantic request/response schemas
│   │   ├── auth.py               # Auth schemas
│   │   └── task.py               # Task schemas
│   ├── routers/                  # API route handlers
│   │   ├── auth.py               # Authentication endpoints
│   │   └── tasks.py              # Task CRUD endpoints
│   ├── middleware/               # Custom middleware
│   │   └── auth.py               # JWT verification
│   ├── services/                 # Business logic
│   │   ├── auth_service.py       # Authentication logic
│   │   └── task_service.py       # Task operations
│   └── utils/                    # Utility functions
│       ├── security.py           # Password hashing, JWT
│       └── validators.py         # Input validation
├── tests/                        # Test suite
│   ├── test_auth.py
│   └── test_tasks.py
└── requirements.txt              # Python dependencies
```

**Key Responsibilities**:
- Expose RESTful API endpoints
- Verify JWT tokens on protected routes
- Validate request payloads
- Enforce authorization rules
- Execute business logic
- Interact with database via ORM
- Return appropriate HTTP responses
- Handle errors gracefully

### Database Architecture (PostgreSQL)

```sql
-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tasks Table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_complete BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_created_at ON tasks(created_at DESC);
CREATE INDEX idx_users_email ON users(email);
```

**Key Responsibilities**:
- Store user credentials securely
- Store task data persistently
- Enforce referential integrity
- Provide ACID transaction guarantees
- Support efficient queries via indexes
- Cascade delete tasks when user deleted

## Data Flow Diagrams

### User Registration Flow

```
┌──────┐                ┌──────────┐              ┌─────────┐              ┌──────────┐
│ User │                │ Frontend │              │ Backend │              │ Database │
└──┬───┘                └────┬─────┘              └────┬────┘              └────┬─────┘
   │                         │                         │                        │
   │ 1. Enter email/password │                         │                        │
   ├────────────────────────>│                         │                        │
   │                         │                         │                        │
   │                         │ 2. POST /api/auth/signup│                        │
   │                         │    {email, password}    │                        │
   │                         ├────────────────────────>│                        │
   │                         │                         │                        │
   │                         │                         │ 3. Check email exists  │
   │                         │                         ├───────────────────────>│
   │                         │                         │                        │
   │                         │                         │ 4. Email available     │
   │                         │                         │<───────────────────────┤
   │                         │                         │                        │
   │                         │                         │ 5. Hash password       │
   │                         │                         │    (bcrypt)            │
   │                         │                         │                        │
   │                         │                         │ 6. INSERT user record  │
   │                         │                         ├───────────────────────>│
   │                         │                         │                        │
   │                         │                         │ 7. User created        │
   │                         │                         │<───────────────────────┤
   │                         │                         │                        │
   │                         │                         │ 8. Generate JWT token  │
   │                         │                         │    (user_id in payload)│
   │                         │                         │                        │
   │                         │ 9. 201 Created          │                        │
   │                         │    {token, user}        │                        │
   │                         │<────────────────────────┤                        │
   │                         │                         │                        │
   │                         │ 10. Store token         │                        │
   │                         │     (localStorage)      │                        │
   │                         │                         │                        │
   │ 11. Redirect to tasks   │                         │                        │
   │<────────────────────────┤                         │                        │
```

### User Authentication Flow (Signin)

```
┌──────┐                ┌──────────┐              ┌─────────┐              ┌──────────┐
│ User │                │ Frontend │              │ Backend │              │ Database │
└──┬───┘                └────┬─────┘              └────┬────┘              └────┬─────┘
   │                         │                         │                        │
   │ 1. Enter email/password │                         │                        │
   ├────────────────────────>│                         │                        │
   │                         │                         │                        │
   │                         │ 2. POST /api/auth/signin│                        │
   │                         │    {email, password}    │                        │
   │                         ├────────────────────────>│                        │
   │                         │                         │                        │
   │                         │                         │ 3. SELECT user by email│
   │                         │                         ├───────────────────────>│
   │                         │                         │                        │
   │                         │                         │ 4. User record         │
   │                         │                         │<───────────────────────┤
   │                         │                         │                        │
   │                         │                         │ 5. Verify password     │
   │                         │                         │    (bcrypt compare)    │
   │                         │                         │                        │
   │                         │                         │ 6. Generate JWT token  │
   │                         │                         │    (user_id in payload)│
   │                         │                         │                        │
   │                         │ 7. 200 OK               │                        │
   │                         │    {token, user}        │                        │
   │                         │<────────────────────────┤                        │
   │                         │                         │                        │
   │                         │ 8. Store token          │                        │
   │                         │    (localStorage)       │                        │
   │                         │                         │                        │
   │ 9. Redirect to tasks    │                         │                        │
   │<────────────────────────┤                         │                        │
```

### Task Creation Flow

```
┌──────┐                ┌──────────┐              ┌─────────┐              ┌──────────┐
│ User │                │ Frontend │              │ Backend │              │ Database │
└──┬───┘                └────┬─────┘              └────┬────┘              └────┬─────┘
   │                         │                         │                        │
   │ 1. Enter task details   │                         │                        │
   ├────────────────────────>│                         │                        │
   │                         │                         │                        │
   │                         │ 2. POST /api/{user_id}/tasks                     │
   │                         │    Authorization: Bearer <JWT>                   │
   │                         │    {title, description} │                        │
   │                         ├────────────────────────>│                        │
   │                         │                         │                        │
   │                         │                         │ 3. Verify JWT token    │
   │                         │                         │    Extract user_id     │
   │                         │                         │                        │
   │                         │                         │ 4. Validate user_id    │
   │                         │                         │    matches URL param   │
   │                         │                         │                        │
   │                         │                         │ 5. Validate payload    │
   │                         │                         │    (title 1-200 chars) │
   │                         │                         │                        │
   │                         │                         │ 6. INSERT task record  │
   │                         │                         │    (user_id, title,    │
   │                         │                         │     description)       │
   │                         │                         ├───────────────────────>│
   │                         │                         │                        │
   │                         │                         │ 7. Task created        │
   │                         │                         │<───────────────────────┤
   │                         │                         │                        │
   │                         │ 8. 201 Created          │                        │
   │                         │    {task}               │                        │
   │                         │<────────────────────────┤                        │
   │                         │                         │                        │
   │                         │ 9. Update UI            │                        │
   │                         │    Add task to list     │                        │
   │                         │                         │                        │
   │ 10. See new task        │                         │                        │
   │<────────────────────────┤                         │                        │
```

### Task List Retrieval Flow

```
┌──────┐                ┌──────────┐              ┌─────────┐              ┌──────────┐
│ User │                │ Frontend │              │ Backend │              │ Database │
└──┬───┘                └────┬─────┘              └────┬────┘              └────┬─────┘
   │                         │                         │                        │
   │ 1. Navigate to tasks    │                         │                        │
   ├────────────────────────>│                         │                        │
   │                         │                         │                        │
   │                         │ 2. GET /api/{user_id}/tasks                      │
   │                         │    Authorization: Bearer <JWT>                   │
   │                         ├────────────────────────>│                        │
   │                         │                         │                        │
   │                         │                         │ 3. Verify JWT token    │
   │                         │                         │    Extract user_id     │
   │                         │                         │                        │
   │                         │                         │ 4. Validate user_id    │
   │                         │                         │    matches URL param   │
   │                         │                         │                        │
   │                         │                         │ 5. SELECT tasks        │
   │                         │                         │    WHERE user_id = ?   │
   │                         │                         │    ORDER BY created_at │
   │                         │                         ├───────────────────────>│
   │                         │                         │                        │
   │                         │                         │ 6. Task records        │
   │                         │                         │<───────────────────────┤
   │                         │                         │                        │
   │                         │ 7. 200 OK               │                        │
   │                         │    {tasks: [...]}       │                        │
   │                         │<────────────────────────┤                        │
   │                         │                         │                        │
   │                         │ 8. Render task list     │                        │
   │                         │                         │                        │
   │ 9. View tasks           │                         │                        │
   │<────────────────────────┤                         │                        │
```

## Authentication Flow (Better Auth + JWT)

### JWT Token Structure

```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "iat": 1704067200,
    "exp": 1704672000
  },
  "signature": "HMACSHA256(base64UrlEncode(header) + '.' + base64UrlEncode(payload), BETTER_AUTH_SECRET)"
}
```

### Token Lifecycle

1. **Token Generation** (Backend)
   - User successfully authenticates (signup or signin)
   - Backend generates JWT with user_id in payload
   - Token signed with `BETTER_AUTH_SECRET` environment variable
   - Token expiration set to 7 days from issuance
   - Token returned to frontend in response

2. **Token Storage** (Frontend)
   - Frontend receives token from authentication response
   - Token stored in browser localStorage or sessionStorage
   - Better Auth library manages token storage automatically

3. **Token Usage** (Frontend)
   - Every API request includes token in Authorization header
   - Format: `Authorization: Bearer <token>`
   - Better Auth client automatically attaches token to requests

4. **Token Verification** (Backend)
   - Middleware intercepts all protected route requests
   - Extracts token from Authorization header
   - Verifies signature using `BETTER_AUTH_SECRET`
   - Checks token expiration
   - Extracts user_id from payload
   - Attaches user_id to request context

5. **Token Expiration**
   - Tokens expire after 7 days of inactivity
   - Expired token requests return 401 Unauthorized
   - Frontend detects 401 and redirects to signin page
   - User must re-authenticate to obtain new token

### Authorization Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    Protected API Request                     │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              1. Extract JWT from Authorization Header        │
│                 Authorization: Bearer <token>                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              2. Verify Token Signature                       │
│                 HMACSHA256(token, SECRET)                    │
└─────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌───────────┐           ┌──────────────┐
        │  Invalid  │           │    Valid     │
        │ Signature │           │  Signature   │
        └─────┬─────┘           └──────┬───────┘
              │                        │
              ▼                        ▼
      ┌──────────────┐      ┌─────────────────────┐
      │ 401          │      │ 3. Check Expiration │
      │ Unauthorized │      └──────────┬──────────┘
      └──────────────┘                 │
                            ┌──────────┴──────────┐
                            │                     │
                            ▼                     ▼
                    ┌──────────┐          ┌──────────┐
                    │ Expired  │          │  Valid   │
                    └────┬─────┘          └────┬─────┘
                         │                     │
                         ▼                     ▼
                 ┌──────────────┐    ┌─────────────────────┐
                 │ 401          │    │ 4. Extract user_id  │
                 │ Unauthorized │    │    from payload     │
                 └──────────────┘    └──────────┬──────────┘
                                                 │
                                                 ▼
                                     ┌─────────────────────┐
                                     │ 5. Validate user_id │
                                     │    matches URL      │
                                     └──────────┬──────────┘
                                                │
                                     ┌──────────┴──────────┐
                                     │                     │
                                     ▼                     ▼
                             ┌──────────┐          ┌──────────┐
                             │ Mismatch │          │  Match   │
                             └────┬─────┘          └────┬─────┘
                                  │                     │
                                  ▼                     ▼
                          ┌──────────────┐    ┌─────────────────┐
                          │ 403          │    │ 6. Execute      │
                          │ Forbidden    │    │    Request      │
                          └──────────────┘    └─────────────────┘
```

### Shared Secret Configuration

Both frontend and backend must share the same secret for JWT signing/verification:

**Backend (.env)**:
```
BETTER_AUTH_SECRET=your-secure-random-secret-here
DATABASE_URL=postgresql://user:pass@host/db
```

**Frontend (.env.local)**:
```
NEXT_PUBLIC_API_URL=https://api.example.com
BETTER_AUTH_SECRET=your-secure-random-secret-here
```

**Security Requirements**:
- Secret must be at least 32 characters
- Secret must be randomly generated
- Secret must never be committed to version control
- Secret must be stored in environment variables only
- Same secret used by both frontend and backend

## Spec-Driven Development Workflow

### Development Process

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Write Specification                    │
│                                                              │
│  • Define user stories and acceptance criteria              │
│  • Specify functional requirements                          │
│  • Define success criteria                                  │
│  • Document assumptions and constraints                     │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    2. Validate Specification                 │
│                                                              │
│  • Check completeness (all mandatory sections)              │
│  • Verify testability (requirements are unambiguous)        │
│  • Confirm measurability (success criteria quantifiable)    │
│  • Resolve [NEEDS CLARIFICATION] markers                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    3. Generate Plan (/sp.plan)               │
│                                                              │
│  • Claude Code analyzes specification                       │
│  • Generates technical architecture                         │
│  • Identifies components and dependencies                   │
│  • Creates implementation strategy                          │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    4. Generate Tasks (/sp.tasks)             │
│                                                              │
│  • Break plan into actionable tasks                         │
│  • Define task dependencies                                 │
│  • Specify acceptance criteria per task                     │
│  • Order tasks by priority                                  │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    5. Implement (/sp.implement)              │
│                                                              │
│  • Claude Code generates code from tasks                    │
│  • Executes tasks in dependency order                       │
│  • Runs tests for each task                                 │
│  • Validates acceptance criteria                            │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    6. Refine and Iterate                     │
│                                                              │
│  • If output incorrect, refine specification                │
│  • Update requirements for clarity                          │
│  • Re-run generation process                                │
│  • Document iterations in PHRs                              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    7. Deploy and Validate                    │
│                                                              │
│  • Deploy frontend to Vercel                                │
│  • Deploy backend API                                       │
│  • Validate against success criteria                        │
│  • Create demo video                                        │
└─────────────────────────────────────────────────────────────┘
```

### Constraint: No Manual Coding

**Rule**: You cannot write code manually. You must refine the specification until Claude Code generates the correct output.

**Process**:
1. Write detailed, unambiguous specification
2. Run Claude Code generation
3. If output is incorrect:
   - Identify what was unclear in the spec
   - Refine the specification (not the code)
   - Re-run generation
4. Repeat until correct output achieved

**Documentation**: All prompts, iterations, and refinements must be documented in Prompt History Records (PHRs).

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                         Vercel CDN                           │
│                    (Frontend Hosting)                        │
│                                                              │
│  • Global edge network                                      │
│  • Automatic HTTPS                                          │
│  • Next.js optimization                                     │
│  • Environment variables                                    │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │ API Requests
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API Server                        │
│                   (Cloud Provider TBD)                       │
│                                                              │
│  • FastAPI application                                      │
│  • HTTPS endpoint                                           │
│  • Environment variables                                    │
│  • CORS configuration                                       │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │ Database Connection
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Neon PostgreSQL                           │
│                  (Serverless Database)                       │
│                                                              │
│  • Automatic scaling                                        │
│  • Connection pooling                                       │
│  • Backup and recovery                                      │
│  • SSL/TLS encryption                                       │
└─────────────────────────────────────────────────────────────┘
```

### Environment Configuration

**Frontend (Vercel)**:
- `NEXT_PUBLIC_API_URL`: Backend API base URL
- `BETTER_AUTH_SECRET`: JWT signing secret

**Backend**:
- `DATABASE_URL`: Neon PostgreSQL connection string
- `BETTER_AUTH_SECRET`: JWT signing secret (must match frontend)
- `CORS_ORIGINS`: Allowed frontend origins

**Database (Neon)**:
- Automatic provisioning via Neon dashboard
- Connection string provided by Neon
- SSL/TLS enabled by default

## Security Architecture

### Defense in Depth

1. **Transport Layer**: HTTPS for all communication
2. **Authentication Layer**: JWT token verification
3. **Authorization Layer**: User ID validation
4. **Data Layer**: Parameterized queries (SQL injection prevention)
5. **Application Layer**: Input validation and sanitization

### Security Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                      Public Internet                         │
└──────────────────────────┬───────────────────────────────────┘
                           │ HTTPS Only
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Vercel)                         │
│  Security: Client-side validation, XSS prevention            │
└──────────────────────────┬───────────────────────────────────┘
                           │ JWT Token Required
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Backend API (FastAPI)                     │
│  Security: JWT verification, authorization checks            │
└──────────────────────────┬───────────────────────────────────┘
                           │ Parameterized Queries
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    Database (Neon)                           │
│  Security: Encrypted at rest, SSL/TLS, access control       │
└─────────────────────────────────────────────────────────────┘
```

## Performance Considerations

### Optimization Strategies

1. **Database Indexing**: Indexes on user_id and created_at for fast queries
2. **Connection Pooling**: Reuse database connections
3. **Lazy Loading**: Load tasks only when needed
4. **Optimistic UI Updates**: Update UI before server confirmation
5. **Caching**: Browser caching for static assets

### Scalability Approach

- **Horizontal Scaling**: Add more backend instances as needed
- **Database Scaling**: Neon automatically scales with demand
- **CDN Distribution**: Vercel edge network for global performance
- **Stateless Backend**: No server-side session storage (JWT-based)

## References

- **Main Specification**: `specs/001-fullstack-web-app/spec.md`
- **API Endpoints**: `specs/001-fullstack-web-app/api/rest-endpoints.md`
- **Database Schema**: `specs/001-fullstack-web-app/database/schema.md`
- **Authentication Details**: `specs/001-fullstack-web-app/features/authentication.md`
- **Task CRUD Details**: `specs/001-fullstack-web-app/features/task-crud.md`
