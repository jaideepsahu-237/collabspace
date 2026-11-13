# Collaborative Multi-Tenant Document Editor — V1

## 1. Project Overview

A simplified Google Docs-style collaborative document editor designed to demonstrate backend engineering concepts such as authentication, authorization, multi-tenancy, PostgreSQL, Redis, WebSockets, and concurrent document editing.

The application allows users to create private documents and explicitly share them with existing registered users as either viewers or editors.

---

## 2. V1 Goal

Build a working end-to-end application with:

- User registration and authentication
- Multi-tenant architecture
- Strict tenant isolation
- Private document ownership
- Document CRUD operations
- Sharing with existing registered users
- Viewer and editor permissions
- Real-time collaborative editing
- WebSocket communication
- Redis-based real-time coordination
- PostgreSQL persistence

The goal is **not** to reproduce every Google Docs feature. V1 should establish a clean and extensible foundation.

---

## 3. Core User Flow

### Registration

A new user can create an account.

```text
User
  |
  v
Sign Up
  |
  v
Account Created
  |
  v
Login
```

### Login

An existing user logs in and receives an authentication token.

```text
Login
  |
  v
Authentication
  |
  v
JWT / Access Token
  |
  v
Authenticated Application
```

### Create Document

Every new document belongs to the authenticated user who created it.

```text
User A
  |
  +-- Create Document
          |
          v
      Document 1
      Owner: User A
      Access: Private
```

### Share Document

The owner can search for an existing registered user and share the document.

```text
User A (Owner)
      |
      | Share Document
      v
Search Existing User
      |
      +------ User B -> Viewer
      |
      +------ User C -> Editor
```

V1 does **not** include email invitations.

If the target user does not have an account:

```text
User not found.
This document can only be shared with existing users in V1.
```

---

## 4. Functional Requirements

### 4.1 Authentication

The system must support:

- User registration
- User login
- Logout/token invalidation strategy as appropriate
- Password hashing
- JWT/access-token based authentication
- Authenticated API access

Unauthenticated users must not access protected application resources.

---

### 4.2 Multi-Tenancy

Users belong to a tenant/organization.

Example:

```text
Tenant A
├── Alice
├── Bob
└── Documents

Tenant B
├── Charlie
├── David
└── Documents
```

Tenant A users must not automatically gain access to Tenant B's data.

Every tenant-scoped resource must be validated against the authenticated user's tenant.

### Important rule

Being part of the same tenant does **not** automatically grant access to another user's private document.

Document access is controlled separately through ownership and document permissions.

---

## 5. Document Ownership

A document has exactly one owner in V1.

When a user creates a document:

```text
Document
├── owner_id = authenticated_user
├── tenant_id = authenticated_user.tenant_id
└── access = private
```

### Default behavior

New documents are private.

Only the owner can:

- View the document
- Edit the document
- Delete the document
- Share the document
- Change sharing permissions

---

## 6. Document Permissions

V1 supports three roles:

| Role | Read | Edit | Delete | Share |
|------|------|------|--------|-------|
| Owner | Yes | Yes | Yes | Yes |
| Editor | Yes | Yes | No | No |
| Viewer | Yes | No | No | No |

### Permission rules

#### Owner

The owner has full control over the document.

#### Editor

An editor can modify the document but cannot change ownership or sharing permissions.

#### Viewer

A viewer can read the document but cannot modify it.

---

## 7. Sharing Model

Documents are shared explicitly.

Example:

```text
Document: Project Plan

Owner:
  Alice

Shared With:
  Bob      -> Editor
  Charlie  -> Viewer
```

A user should not be able to share a document unless they have permission to manage sharing. In V1, this means the owner.

### Sharing an existing user

Conceptually:

```http
POST /api/documents/{document_id}/share
```

Example request:

```json
{
  "user_id": 42,
  "role": "editor"
}
```

The backend must validate:

1. Requester is authenticated.
2. Document exists.
3. Requester owns the document.
4. Target user exists.
5. Permission is valid.
6. Permission is created or updated safely.

---

## 8. Document Management

V1 should provide:

```text
Create Document
List Documents
Get Document
Update Document
Delete Document
```

Suggested endpoints:

```http
POST   /api/documents
GET    /api/documents
GET    /api/documents/{document_id}
PATCH  /api/documents/{document_id}
DELETE /api/documents/{document_id}
```

The document list should contain documents that the current user owns or has been granted access to.

---

## 9. Real-Time Collaboration

Users with editor access should be able to edit the same document concurrently.

Example:

```text
                 Document 123
                     |
          +----------+----------+
          |          |          |
        Alice       Bob       Charlie
       Editor     Editor       Viewer
          |          |           |
          +----------+-----------+
                     |
                 WebSocket
```

When Alice changes the document:

```text
Alice
  |
  | WebSocket operation
  v
FastAPI
  |
  v
Collaboration Layer
  |
  v
Redis
  |
  +----> Bob
  |
  +----> Other connected editors/viewers
```

Changes should appear to other connected users without requiring page refresh.

---

## 10. WebSocket Responsibilities

WebSockets are responsible for real-time collaboration.

Suggested endpoint:

```text
WS /ws/documents/{document_id}
```

When a user connects, the backend should verify:

1. User is authenticated.
2. Document exists.
3. User belongs to the appropriate tenant.
4. User has permission to access the document.

The server should reject unauthorized WebSocket connections.

---

## 11. Redis Responsibilities

Redis can be used for real-time collaboration infrastructure.

### Redis Pub/Sub

Used to distribute document events between application instances.

```text
FastAPI Instance 1
       |
       v
Redis Pub/Sub
       |
       +------> FastAPI Instance 2
       |
       +------> FastAPI Instance 3
```

This becomes important when the application is horizontally scaled.

### Presence

Redis can also maintain short-lived presence information such as:

```text
Document 123

Alice -> editing
Bob   -> editing
Charlie -> viewing
```

Presence data does not need to be the permanent source of truth.

---

## 12. PostgreSQL Responsibilities

PostgreSQL is the persistent source of truth for application data.

It should store:

- Tenants
- Users
- Documents
- Document permissions
- Optional document revisions

---

## 13. Initial Database Model

### Tenant

```text
tenants
-------
id
name
created_at
updated_at
```

### User

```text
users
-----
id
tenant_id
email
password_hash
name
created_at
updated_at
```

### Document

```text
documents
---------
id
tenant_id
owner_id
title
content
created_at
updated_at
```

### Document Permission

```text
document_permissions
--------------------
id
document_id
user_id
role
created_at
updated_at
```

### Optional Revision

If basic version history is included in V1:

```text
document_revisions
------------------
id
document_id
version
content
created_by
created_at
```

---

## 14. Tenant Isolation

Tenant isolation is a critical security requirement.

Bad:

```sql
SELECT *
FROM documents
WHERE id = :document_id;
```

The query must be scoped appropriately.

For example:

```sql
SELECT *
FROM documents
WHERE id = :document_id
  AND tenant_id = :tenant_id;
```

Application authorization must also verify ownership or explicit document permission.

### Security principle

Never trust a `tenant_id` supplied by the client.

The tenant context should be derived from the authenticated user/session.

---

## 15. Suggested Architecture

```text
                    +----------------+
                    |    React UI    |
                    +-------+--------+
                            |
                  REST / WebSocket
                            |
                            v
                    +---------------+
                    |    FastAPI    |
                    +-------+-------+
                            |
             +--------------+--------------+
             |                             |
             v                             v
      +-------------+               +-------------+
      | PostgreSQL  |               |    Redis    |
      |             |               |             |
      | Users       |               | Pub/Sub     |
      | Tenants     |               | Presence    |
      | Documents   |               |             |
      | Permissions |               |             |
      +-------------+               +-------------+
```

---

## 16. Proposed Technology Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT authentication
- Pytest

### Database

- PostgreSQL

### Real-Time

- WebSocket
- Redis
- Redis Pub/Sub

### Frontend

- React
- Basic document editor

### Development

- Git
- Docker
- Docker Compose

Nginx can be introduced later if needed.

---

## 17. Concurrent Editing Strategy

Concurrent editing is the most technically challenging part of the project.

V1 should start with a **simple, well-defined synchronization model** rather than attempting to implement Google Docs-level collaboration immediately.

Possible future approaches include:

- Operational Transformation (OT)
- CRDTs

For the first implementation, the collaboration protocol should be kept simple and designed so it can later be replaced or upgraded.

The system must avoid blindly allowing the last database write to overwrite another user's changes.

---

## 18. Authorization Rules

Every protected operation should answer:

```text
Who is the user?
        |
        v
Which tenant does the user belong to?
        |
        v
Does the resource belong to that tenant?
        |
        v
Does the user have permission?
        |
        v
Allow / Reject
```

Example:

```text
Alice requests Document 123
        |
        v
Authenticated?       YES
        |
        v
Correct tenant?      YES
        |
        v
Owner / Editor / Viewer?
        |
        v
Apply appropriate permission
```

---

## 19. V1 API Overview

### Authentication

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

### Documents

```http
POST   /api/documents
GET    /api/documents
GET    /api/documents/{id}
PATCH  /api/documents/{id}
DELETE /api/documents/{id}
```

### Sharing

```http
POST   /api/documents/{id}/share
GET    /api/documents/{id}/permissions
PATCH  /api/documents/{id}/permissions/{user_id}
DELETE /api/documents/{id}/permissions/{user_id}
```

### Real-Time

```text
WS /ws/documents/{document_id}
```

The exact API design can be refined during implementation.

---

## 20. V1 Scope — Included

- [x] User registration
- [x] User login
- [x] Authentication
- [x] Tenant model
- [x] Tenant isolation
- [x] User model
- [x] Document creation
- [x] Document ownership
- [x] Private documents by default
- [x] Document CRUD
- [x] Existing-user sharing
- [x] Viewer permission
- [x] Editor permission
- [x] WebSocket connection
- [x] Real-time document updates
- [x] Redis Pub/Sub
- [x] Basic user presence
- [x] PostgreSQL persistence

---

## 21. V1 Scope — Excluded

The following are intentionally excluded from V1:

- Email invitations
- Public document links
- Anonymous document access
- Google/GitHub OAuth
- Comments
- Document suggestions
- Offline editing
- Advanced formatting
- Full Google Docs editor functionality
- Advanced version restoration
- Email notifications
- Push notifications
- Complex document search
- Enterprise billing/subscriptions

These can be considered after V1 is stable.

---

## 22. Definition of Done

V1 is considered complete when the following scenario works:

```text
1. Alice registers.
2. Alice logs in.
3. Alice creates a document.
4. The document is private.
5. Alice creates another user, Bob, or shares with an existing Bob account.
6. Alice shares the document with Bob as Editor.
7. Bob logs in.
8. Bob can see the shared document.
9. Bob can edit the document.
10. Alice sees Bob's changes in real time.
11. Alice and Bob can be connected to the same document simultaneously.
12. A Viewer can read but cannot edit.
13. A user without permission cannot access the document.
14. A user from another tenant cannot access tenant-scoped data.
15. Unauthorized REST and WebSocket requests are rejected.
16. Document data remains persisted in PostgreSQL.
```

---

## 23. Development Order

Build the project in this order:

```text
Phase 1
Project setup
    ↓
FastAPI + PostgreSQL + Docker
    ↓
Database migrations

Phase 2
Authentication
    ↓
Users
    ↓
Tenants
    ↓
JWT

Phase 3
Documents
    ↓
Ownership
    ↓
CRUD
    ↓
Authorization

Phase 4
Sharing
    ↓
Viewer
    ↓
Editor
    ↓
Permission validation

Phase 5
React frontend
    ↓
Login
    ↓
Dashboard
    ↓
Document list
    ↓
Document editor

Phase 6
WebSocket
    ↓
Real-time updates
    ↓
Redis Pub/Sub
    ↓
Presence

Phase 7
Concurrent editing
    ↓
Conflict handling
    ↓
Testing
    ↓
Dockerized V1
```

---

## 24. Important Engineering Principles

Throughout V1:

1. **Authentication is not authorization.**
2. Never trust client-provided tenant IDs.
3. Every document operation must verify access.
4. Private is the default document state.
5. Sharing must be explicit.
6. Viewer and editor permissions must be enforced on the backend, not just hidden in the UI.
7. WebSocket connections must perform authorization.
8. PostgreSQL is the durable source of truth.
9. Redis is used for real-time coordination, not as the permanent document store.
10. Avoid premature microservices; build V1 as a clean modular monolith.
11. Write tests for tenant isolation and authorization.
12. Design the collaboration layer so the synchronization strategy can evolve later.

---

## 25. V1 Success Criteria

The project should demonstrate practical understanding of:

```text
Python / FastAPI
        +
REST APIs
        +
JWT Authentication
        +
Authorization
        +
PostgreSQL
        +
SQLAlchemy
        +
Multi-Tenancy
        +
Redis
        +
WebSockets
        +
Concurrency
        +
React
        +
Docker
        +
Testing
```

The primary objective is to build a **working, secure, understandable V1**, not to maximize the number of features.
