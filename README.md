# CollabSpace

**A Multi-Tenant Real-Time Collaborative Document Editor**

CollabSpace is a Google Docs-inspired collaborative document editing platform designed to explore backend engineering concepts, including authentication, authorization, multi-tenancy, real-time communication, and concurrent editing.

The platform allows users to create private documents and explicitly share them with other registered users with different access permissions.

## Project Goals

- Secure user authentication and authorization.
- Multi-tenant architecture with strict tenant isolation.
- Private document ownership and document management.
- Explicit document sharing with Viewer and Editor permissions.
- Real-time collaborative editing.
- Scalable real-time communication using WebSockets and Redis.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Migrations | Alembic |
| Validation | Pydantic |
| Authentication | JWT |
| Real-Time Communication | WebSockets |
| Message Coordination | Redis |
| Frontend (Planned) | React |
| Testing | Pytest |
| Containerization (Planned) | Docker |

## Architecture

CollabSpace follows a modular monolithic architecture.

```text
                 React Frontend
                       |
                 REST / WebSocket
                       |
                    FastAPI
                       |
             +---------+---------+
             |                   |
         PostgreSQL             Redis
             |                   |
       Persistent Data      Real-Time Events
```

## Project Structure

```text
CollabSpace/
│
├── collabspace-backend/
│   ├── app/
│   ├── alembic/
│   ├── alembic.ini
│   └── requirements.txt
│
├── docs/
│   └── PROJECT_OVERVIEW.md
│
├── README.md
└── .gitignore
```

## Development Status

**Current Phase: Backend Development**

The project is being developed incrementally.

Planned development phases:

1. Project setup and database configuration.
2. Authentication and multi-tenancy.
3. Document management and ownership.
4. Document sharing and authorization.
5. Frontend development.
6. WebSocket and Redis integration.
7. Concurrent editing and testing.

Features will be marked complete as they are implemented and tested.

## Getting Started

### Backend Setup

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/CollabSpace.git
cd CollabSpace
```

Navigate to the backend:

```bash
cd collabspace-backend
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your environment variables using `.env.example` (once available).

Run database migrations:

```bash
alembic upgrade head
```

Start the development server from the repository's backend directory:

```bash
python -m uvicorn app.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

## Documentation

For detailed functional requirements, database design, authorization rules, API specifications, architecture, and development roadmap, see:

[Project Overview](docs/PROJECT_OVERVIEW.md)

## Engineering Principles

- Authentication is not authorization.
- Never trust client-provided tenant IDs.
- Enforce authorization at the backend.
- Documents are private by default.
- Sharing must be explicit.
- PostgreSQL is the persistent source of truth.
- Redis handles real-time coordination.
- Build a secure and maintainable modular monolith.

---

**Project:** CollabSpace  
**Version:** V1  
**Status:** In Development