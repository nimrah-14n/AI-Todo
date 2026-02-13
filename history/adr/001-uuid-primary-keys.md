# ADR-001: Use UUID Primary Keys for Database Schema

**Status**: Accepted
**Date**: 2026-01-15
**Context**: Phase II Full-Stack Web Application
**Deciders**: ALCL, Claude Code (Analysis)

---

## Context and Problem Statement

The initial constitution specified `integer` primary keys for database tables. During Phase II implementation planning, the data model was designed with UUID primary keys. The `/sp.analyze` command detected this as a constitution violation requiring resolution.

**Decision Required**: Should we use integer auto-increment IDs or UUID primary keys for the database schema?

---

## Decision Drivers

1. **Security**: Prevent enumeration attacks on API endpoints
2. **Distributed Systems**: Phase V requires multi-region deployment with Kafka and Dapr
3. **Scalability**: Support horizontal scaling without ID collision
4. **Modern Best Practices**: Industry standard for cloud-native applications
5. **Future-Proofing**: Enable features like offline-first sync, data merging, and replication

---

## Considered Options

### Option 1: Integer Auto-Increment IDs (Original Constitution)

**Pros**:
- Smaller storage footprint (4-8 bytes vs 16 bytes)
- Simpler to read and debug (e.g., task ID 42 vs `550e8400-e29b-41d4-a716-446655440000`)
- Slightly faster indexing and joins
- Sequential ordering implicit in ID

**Cons**:
- **Security Risk**: Sequential IDs enable enumeration attacks (attacker can guess valid IDs)
- **Distributed Systems**: Requires central ID generation, creating bottleneck and single point of failure
- **Scalability**: Cannot generate IDs independently across multiple database instances
- **Data Merging**: Conflicts when merging data from different sources (Phase V requirement)
- **Horizontal Scaling**: Difficult to shard database without ID collisions

### Option 2: UUID Primary Keys (Implemented in Phase II)

**Pros**:
- **Security**: Non-sequential IDs prevent enumeration attacks
- **Distributed Systems**: Each node can generate IDs independently without coordination
- **Scalability**: No central bottleneck for ID generation
- **Data Merging**: Conflict-free merging across multiple databases (critical for Phase V Kafka/Dapr)
- **Offline-First**: Clients can generate IDs before syncing to server
- **Modern Standard**: Industry best practice for cloud-native, microservices architectures
- **Future-Proof**: Supports multi-region, multi-master replication

**Cons**:
- Larger storage (16 bytes vs 4-8 bytes) - negligible impact at Phase II scale
- Less human-readable in logs and debugging
- Slightly slower indexing (marginal, not measurable at Phase II scale)

---

## Decision Outcome

**Chosen Option**: Option 2 - UUID Primary Keys

**Rationale**:

1. **Phase V Alignment**: The constitution explicitly requires distributed systems with Kafka event streaming and Dapr runtime abstraction (Phase V). UUIDs are essential for conflict-free event sourcing and multi-region deployments.

2. **Security First**: Non-sequential IDs prevent enumeration attacks where attackers iterate through `/api/{user_id}/tasks/1`, `/api/{user_id}/tasks/2`, etc. to discover other users' tasks.

3. **Scalability**: UUIDs enable horizontal scaling without coordination overhead. Each backend instance can generate IDs independently.

4. **Modern Best Practice**: UUID primary keys are the industry standard for:
   - Microservices architectures
   - Event-driven systems
   - Cloud-native applications
   - Distributed databases (Neon PostgreSQL supports distributed queries)

5. **Negligible Tradeoffs**: The storage and performance costs are insignificant at Phase II scale (< 10,000 tasks per NFR-008). Modern databases handle UUID indexing efficiently.

6. **Constitution Amendment**: Updated constitution v1.1.0 to reflect UUID schema with documented rationale.

---

## Consequences

### Positive

- **Security**: API endpoints resistant to enumeration attacks
- **Phase V Ready**: No schema migration needed when adding Kafka/Dapr
- **Scalability**: Can add read replicas and horizontal sharding without ID conflicts
- **Developer Experience**: SQLModel/Pydantic handle UUIDs natively with `uuid4()` generation

### Negative

- **Debugging**: IDs less readable in logs (mitigated by structured logging with task titles)
- **Storage**: 12 extra bytes per record (negligible: 12 bytes × 10,000 tasks = 120 KB)

### Neutral

- **Migration**: No migration needed (Phase II is greenfield implementation)
- **API Contracts**: OpenAPI spec already uses `format: uuid` for ID fields

---

## Implementation Notes

### Database Schema (SQLModel)

```python
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    # ...

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id")
    # ...
```

### API Contracts (OpenAPI)

```yaml
parameters:
  UserIdPath:
    name: user_id
    schema:
      type: string
      format: uuid
  TaskIdPath:
    name: id
    schema:
      type: string
      format: uuid
```

### Frontend (TypeScript)

```typescript
interface Task {
  id: string; // UUID as string
  user_id: string;
  // ...
}
```

---

## Related Decisions

- **Field Naming**: Also amended constitution to use `is_complete` instead of `completed` for boolean clarity (follows `is_*` convention common in SQLModel/Pydantic)

---

## References

- Constitution v1.1.0 (amended 2026-01-15)
- Phase II Specification: `specs/001-fullstack-web-app/spec.md`
- Data Model: `specs/001-fullstack-web-app/data-model.md`
- Analysis Report: `/sp.analyze` execution (2026-01-15)
- Phase V Requirements: Kafka, Dapr, multi-region deployment (constitution.md)

---

## Validation

- [x] Constitution updated to v1.1.0 with UUID schema
- [x] Rationale documented in constitution
- [x] Data model already implements UUIDs (no changes needed)
- [x] OpenAPI contracts already use `format: uuid`
- [x] Tasks.md references correct schema (no changes needed)
- [x] ADR created and linked

---

**Status**: ✅ Accepted and Implemented
**Next Review**: Phase V planning (when implementing distributed systems)
