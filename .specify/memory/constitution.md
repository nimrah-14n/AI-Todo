# Evolution of Todo - Hackathon II Constitution

> **Purpose**: Master Spec-Driven Development (SDD) by building a Todo application that evolves from CLI to Cloud-Native AI System.

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)

**You MUST NOT write code manually.** All implementation MUST be generated through Claude Code based on specifications.

- Every feature requires a Markdown Spec before implementation
- Refine the Spec until Claude Code generates correct output
- Process: `Specify → Plan → Tasks → Implement`
- No freestyle coding - specs are the single source of truth
- All code must trace back to a validated task

### II. Test-First Development (TDD)

- Tests written BEFORE implementation
- Red-Green-Refactor cycle strictly enforced
- Every task must have testable acceptance criteria
- No code merges without passing tests

### III. Iterative Evolution

The project follows a strict 5-phase evolution:

| Phase | Description | Core Focus |
|-------|-------------|------------|
| I | In-Memory Console App | Python fundamentals, basic CRUD |
| II | Full-Stack Web App | Next.js, FastAPI, Neon DB, Auth |
| III | AI Chatbot | OpenAI Agents SDK, MCP Server |
| IV | Local Kubernetes | Docker, Minikube, Helm, AIOps |
| V | Cloud Deployment | Kafka, Dapr, GKE/AKS/DOKS |

**Each phase builds on the previous. No skipping phases.**

### IV. Monorepo Architecture

```
hackathon-todo/
├── .spec-kit/                # Spec-Kit configuration
├── specs/                    # Feature specifications
│   ├── features/            # What to build
│   ├── api/                 # API contracts
│   ├── database/            # Schema definitions
│   └── ui/                  # Component specs
├── frontend/                # Next.js application
├── backend/                 # FastAPI server
├── CLAUDE.md               # Agent instructions
└── AGENTS.md               # Cross-agent rules
```

### V. Clean Code & Simplicity

- YAGNI (You Aren't Gonna Need It) - no premature optimization
- Smallest viable diff - no unrelated refactoring
- No hardcoded secrets - use `.env` files
- Every function has a single responsibility
- Code is self-documenting with clear naming

### VI. Observability & Documentation

- Structured logging required
- All decisions documented in ADRs
- Prompt History Records (PHR) for every significant interaction
- README with setup instructions mandatory

---

## Technology Stack (MANDATORY)

### Phase I: Console Application
| Component | Technology |
|-----------|------------|
| Runtime | Python 3.13+ |
| Package Manager | UV |
| AI Assistant | Claude Code |
| Spec Management | Spec-Kit Plus |

### Phase II: Full-Stack Web Application
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16+ (App Router) |
| Backend | Python FastAPI |
| ORM | SQLModel |
| Database | Neon Serverless PostgreSQL |
| Authentication | Better Auth (JWT) |

### Phase III: AI Chatbot
| Component | Technology |
|-----------|------------|
| Chat UI | OpenAI ChatKit |
| AI Framework | OpenAI Agents SDK |
| Tool Protocol | Official MCP SDK |
| State Storage | Neon PostgreSQL |

### Phase IV: Local Kubernetes
| Component | Technology |
|-----------|------------|
| Containerization | Docker (Docker Desktop) |
| AI Docker | Gordon (Docker AI Agent) |
| Orchestration | Minikube |
| Package Manager | Helm Charts |
| AI DevOps | kubectl-ai, Kagent |

### Phase V: Cloud Deployment
| Component | Technology |
|-----------|------------|
| Event Streaming | Kafka (Redpanda/Strimzi) |
| Runtime Abstraction | Dapr |
| Cloud Provider | Azure AKS / Google GKE / Oracle OKE |
| CI/CD | GitHub Actions |

---

## Feature Requirements

### Basic Level (Phases I-III) - REQUIRED
1. **Add Task** - Create new todo items (title, description)
2. **Delete Task** - Remove tasks from the list
3. **Update Task** - Modify existing task details
4. **View Task List** - Display all tasks with status
5. **Mark Complete** - Toggle task completion status

### Intermediate Level (Phase V)
1. Priorities & Tags/Categories (high/medium/low, work/home)
2. Search & Filter (by keyword, status, priority, date)
3. Sort Tasks (by due date, priority, alphabetically)

### Advanced Level (Phase V)
1. Recurring Tasks - Auto-reschedule repeating tasks
2. Due Dates & Time Reminders - Deadlines with notifications

---

## API Contract Standards

### REST Endpoints (Phase II+)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/{user_id}/tasks` | List all tasks |
| POST | `/api/{user_id}/tasks` | Create new task |
| GET | `/api/{user_id}/tasks/{id}` | Get task details |
| PUT | `/api/{user_id}/tasks/{id}` | Update task |
| DELETE | `/api/{user_id}/tasks/{id}` | Delete task |
| PATCH | `/api/{user_id}/tasks/{id}/complete` | Toggle completion |

### Authentication Requirements
- All endpoints require JWT token in `Authorization: Bearer <token>` header
- Requests without token receive `401 Unauthorized`
- Each user only sees/modifies their own tasks
- Shared secret (`BETTER_AUTH_SECRET`) between frontend and backend

### MCP Tools (Phase III+)
| Tool | Purpose | Parameters |
|------|---------|------------|
| `add_task` | Create task | user_id, title, description? |
| `list_tasks` | Get tasks | user_id, status? |
| `complete_task` | Mark complete | user_id, task_id |
| `delete_task` | Remove task | user_id, task_id |
| `update_task` | Modify task | user_id, task_id, title?, description? |

---

## Database Schema

### Users Table
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PRIMARY KEY |
| email | string | UNIQUE, NOT NULL, max 255 chars |
| hashed_password | string | NOT NULL, max 255 chars |
| created_at | timestamp | AUTO |
| updated_at | timestamp | AUTO |

### Tasks Table
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FOREIGN KEY → users.id |
| title | string | NOT NULL, 1-200 chars |
| description | text | NULLABLE, max 1000 chars |
| is_complete | boolean | DEFAULT false |
| created_at | timestamp | AUTO |
| updated_at | timestamp | AUTO |

### Conversation Table (Phase III+)
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PRIMARY KEY |
| user_id | UUID | FOREIGN KEY |
| created_at | timestamp | AUTO |
| updated_at | timestamp | AUTO |

### Message Table (Phase III+)
| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PRIMARY KEY |
| conversation_id | UUID | FOREIGN KEY |
| user_id | UUID | FOREIGN KEY |
| role | enum | 'user' or 'assistant' |
| content | text | NOT NULL |
| created_at | timestamp | AUTO |

### Schema Design Rationale

**UUID Primary Keys** (amended 2026-01-15):
- **Security**: Non-sequential IDs prevent enumeration attacks
- **Distributed Systems**: UUIDs enable conflict-free merging across multiple databases (critical for Phase V)
- **Scalability**: No central ID generation bottleneck
- **Modern Best Practice**: Industry standard for cloud-native applications
- **Future-Proof**: Supports horizontal scaling and multi-region deployments

**Field Naming** (amended 2026-01-15):
- `is_complete` preferred over `completed` for boolean clarity (follows `is_*` convention)
- Aligns with SQLModel/Pydantic naming patterns
- More explicit and self-documenting in code

---

## Development Workflow

### Spec-Kit Lifecycle (MANDATORY)

```
1. /specify  → Capture requirements in speckit.specify
2. /plan     → Generate technical approach in speckit.plan
3. /tasks    → Break into actionable speckit.tasks
4. /implement → Execute code changes via Claude Code
```

### Agent Behavior Rules

1. **Never generate code without a referenced Task ID**
2. **Never modify architecture without updating `speckit.plan`**
3. **Never propose features without updating `speckit.specify`**
4. **Never change approach without updating `speckit.constitution`**
5. **Every code file must link to Task and Spec sections**

### Code Reference Format
```
[Task]: T-001
[From]: speckit.specify §2.1, speckit.plan §3.4
```

### Hierarchy of Truth
```
Constitution > Specify > Plan > Tasks
```

---

## Quality Gates

### Before Code Generation
- [ ] Spec file exists and is approved
- [ ] Plan file reviewed and validated
- [ ] Tasks are atomic and testable
- [ ] Acceptance criteria defined

### Before Merge/Deploy
- [ ] All tests pass
- [ ] No hardcoded secrets
- [ ] Code traces to task ID
- [ ] PHR created for significant work
- [ ] ADR created for architectural decisions

### Performance Standards
- API response: < 200ms p95 latency
- Frontend load: < 3s initial load
- Database queries: indexed appropriately

### Security Requirements
- No secrets in code (use environment variables)
- JWT tokens with expiration
- User data isolation enforced
- Input validation at API boundaries

---

## Event-Driven Architecture (Phase V)

### Kafka Topics
| Topic | Producer | Consumer | Purpose |
|-------|----------|----------|---------|
| `task-events` | Chat API | Recurring Task, Audit | All CRUD operations |
| `reminders` | Chat API | Notification Service | Scheduled triggers |
| `task-updates` | Chat API | WebSocket Service | Real-time sync |

### Dapr Building Blocks
| Block | Use Case |
|-------|----------|
| Pub/Sub | Kafka abstraction |
| State Management | Conversation storage |
| Service Invocation | Frontend → Backend with retries |
| Bindings | Cron triggers for reminders |
| Secrets | API keys, credentials |

---

## Deliverables Checklist

### Required Submissions
- [ ] Public GitHub Repository
- [ ] `/specs` folder with all specifications
- [ ] `CLAUDE.md` with agent instructions
- [ ] `README.md` with setup documentation
- [ ] Demo video (max 90 seconds)
- [ ] Deployed application links

### Phase-Specific Deliverables
| Phase | Deliverable |
|-------|-------------|
| I | Working console app with 5 basic features |
| II | Web app on Vercel + Backend API URL |
| III | Chatbot with MCP tools |
| IV | Minikube deployment + Helm charts |
| V | Cloud deployment + CI/CD pipeline |

---

## Governance

- This Constitution supersedes all other practices
- Amendments require documentation and approval
- All implementations must verify compliance
- Complexity must be justified against YAGNI

**Version**: 1.1.0 | **Ratified**: 2025-12-29 | **Last Amended**: 2026-01-15

## Amendment History

### v1.1.0 (2026-01-15)
- **Changed**: Database schema to use UUID primary keys instead of integer
- **Changed**: Task completion field from `completed` to `is_complete`
- **Added**: Schema Design Rationale section documenting UUID and naming decisions
- **Rationale**: Align with modern cloud-native best practices, support Phase V distributed systems, improve security through non-sequential IDs
- **Impact**: All phases (II-V) benefit from UUID adoption
